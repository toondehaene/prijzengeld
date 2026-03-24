# %%
"""
This script generates fair prize money per category, which is the combination of a dicipline (MS WS MD WD WXD MXD) and a rank (1-12)

The logic is based on some basic principles:

    1. Higher ranked players should get more prize money
        arguments:
        - Not really an argument but just an observation: every sport / competition does it like this, it probably has a good reason.
        - If the goal is to promote people to become better badminton players, it makes sense to reward winning higher ranks more.
        - Better players invest more into becoming better, therefore it's fair they earn more.
        - ... (you can probably write a whole essay about this).

    2. The same total prize money should go to women as to men
        arguments:
        - People can't influence which gender they allign most with.
        - Approximately 50% of the general population is either man or woman.

    3. A club can assign a total budget for the prize money
        arguments:
        - Clubs want to make sure not to run a deficit.

    4. The more people participate in a category, the more prize money
        arguments:
        - The winner had to beat more opponents
        - This category contributed more sign-up money

"""
# %% OPTIONAL: One-shot data scraping and parsing (guarded)
# Set to True to run the scraper and parser once from this script.
# This is intentionally off by default because scraping is network- and time- consuming.
RUN_SCRAPE_AND_PARSE = False

if RUN_SCRAPE_AND_PARSE:
    import time
    # Import the one-shot entry points from the local modules
    # These modules live in the same directory as this script.
    from scrape import scrape_all
    from parse_player_table import parse_all

    # Run the scrape (writes HTML files under ./scrapes/)
    print("Starting one-shot scrape...")
    scrape_all()

    # Parse the scraped HTML into a player table CSV
    print("Parsing scraped pages into player table...")
    df = parse_all()
    timestamp = int(time.time())
    out_path = f"player_table_{timestamp}.csv"
    df.write_csv(out_path)
    print(f"One-shot scrape & parse complete. Wrote {out_path}")



# %% Checking rank distributions
"""
As of reason 3. we want a system where each category gets a weight and based on that weight a proportion of the total budget is assigned.
As of reason 4. we want this weight to increase with the number of participants; i.e. we want a weight per participant where the total weight of a category is just the sum of its participant's weights
As of reason 1. we want this weight to be higher for higher ranked players.

One idea is to have the pariticpant weight depend inversely on the amount of players that have this rank in the overall population. We investigate:
"""
from plotly.io import renderers
import polars as pl

playertablepath = "./player_table_1774367183.csv"

dfplayer = pl.read_csv(playertablepath).rename(
    {
        "Speelsterkte": "rank",
        "Discipline": "discipline",
    }
)
dfplayer.head()

# plotly plot histogram (binned per category 1-12). 6x histogram one for each category
import plotly.express as px

# import plotly.io as pio
# pio.renderers.default = 'notebook'
fig = px.histogram(dfplayer, x="rank", facet_row="discipline", height=1200)
fig.update_yaxes(matches=None)  # Allow independent y-axis scales for each subplot
fig.write_html("./histogram.html", auto_open=True)

# fig.show()

# Calculate the ratio of each rank within each discipline
rank_ratio_by_discipline = (
    dfplayer.group_by("discipline", "rank")
    .agg(pl.len().alias("count"))
    .with_columns(
        (pl.col("count") / pl.col("count").sum().over("discipline")).alias("ratio")
    )
    .sort("discipline", "rank")
).with_columns(
    [
        pl.lit(1.0)
        .truediv(pl.col("ratio"))
        .log1p()
        .alias("weight")  # TODO tune this formula, use log / sqrt normalization?
    ]
)
"""
WHY LOG SCALING? --> open for debate btw
Since the ranks come from an Elo-like system, log scaling for weight calculation makes sense.
In Elo, the probability of winning follows an exponential relationship with rating difference; a 400-point gap always means about 90% win probability,
so skill differences grow exponentially, not linearly. When we invert the frequency of each rank (`1/ratio`) to weight rarer ranks higher,
we're working with something that already has exponential structure.
Without the log, a rank with 0.1% of players gets valued 1000× higher than a 10% rank,
even though Elo treats these differences less drastically.
Taking the log of the inverse frequency brings the weight scaling in line with how Elo's exponential skill progression actually works;
a rank that's 10× rarer gets weighted logarithmically higher,
which reflects how much harder it is to beat players at that level according to Elo's math.
This way, prize allocation respects both how many people signed up and how much more difficult it actually is to win at higher ranks.
"""
rank_ratio_by_discipline.filter(pl.col("rank").eq(1) | pl.col("rank").eq(12))

# %% Load dijlevallei participants and assign weights
"""
Load the dijlevallei participants CSV and use the rank_ratio_by_discipline
weight lookup table to assign weights to each participant.
"""

dijlevallei_path = "./dijlevallei_26_participants.csv"
dfdijlevallei = pl.read_csv(dijlevallei_path)

# Join with rank_ratio_by_discipline to get weights
dfdijlevallei_weighted = (
    dfdijlevallei.join(
        rank_ratio_by_discipline.select(["discipline", "rank", "weight"]),
        on=["discipline", "rank"],
        how="left",
    )
    .with_columns(
        (pl.col("participants") * pl.col("weight")).alias("weight_per_category")
    )
    # Classify disciplines by gender
    .with_columns(
        pl.when(pl.col("discipline").is_in(["MS", "MD", "XDM"]))
        .then(pl.lit("male"))
        .when(pl.col("discipline").is_in(["WS", "WD", "XDW"]))
        .then(pl.lit("female"))
        .alias("gender")
    )
    # Normalize weights within each gender group
    .with_columns(
        (
            pl.col("weight_per_category")
            / pl.col("weight_per_category").sum().over("gender")
        ).alias("normalized_weight_per_gender")
    )
    # Allocate budget: 1250 euros per gender
    .with_columns(
        pl.when(pl.col("gender") == "male")
        .then(pl.col("normalized_weight_per_gender") * 1250)
        .when(pl.col("gender") == "female")
        .then(pl.col("normalized_weight_per_gender") * 1250)
        .alias("prize_money")
    )
)

# Group XDM and XDW by rank as they share the mixed doubles prize pool
dfdijlevallei_weighted = (
    dfdijlevallei_weighted.with_columns(
        pl.when(pl.col("discipline").is_in(["XDM", "XDW"]))
        .then(pl.lit("XD"))
        .otherwise(pl.col("discipline"))
        .alias("discipline_grouped")
    )
    .group_by("discipline_grouped", "rank")
    .agg(
        pl.col("participants").sum().alias("participants"),
        pl.col("weight").first().alias("weight"),
        pl.col("prize_money").sum().alias("prize_money"),
    )
    .rename({"discipline_grouped": "discipline"})
    .sort("discipline", "rank")
)

# Round prize_money towards its mean (subtract mean, round to zero, add back)
dfdijlevallei_weighted = dfdijlevallei_weighted.with_columns(
    (
        pl.col("prize_money").mean().cast(pl.Int64)
        + (
            pl.col("prize_money") - pl.col("prize_money").mean().cast(pl.Int64)
        ).truncate(0)
    ).alias("prize_money")
)

dfdijlevallei_weighted.write_csv("dijlevallei_26_calculated.csv")
print(f"total money to hand out: {dfdijlevallei_weighted.sum().get_column("prize_money").item()}")
dfdijlevallei_weighted


# %%

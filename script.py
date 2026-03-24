"""
This script generates fair price money per category, which is the combination of a dicipline (MS WS MD WD WXD MXD) and a rank (1-12)

The logic is based on some basic principles:

    1. Higher ranked players should get more price money
        arguments:
        - Not really an argument but just an observation: every sport / competition does it like this, it probably has a good reason.
        - If the goal is to promote people to become better badminton players, it makes sense to reward winning higher ranks more.
        - Better players invest more into becoming better, therefore it's fair they earn more.
        - ... (you can probably write a whole essay about this).

    2. The same total price money should go to women as to men
        arguments:
        - People can't influence which gender they allign most with.
        - Approximately 50% of the general population is either man or woman.

    3. A club can assign a total budget for the price money
        arguments:
        - Clubs want to make sure not to run a deficit.

    4. The more people participate in a category, the more price money
        arguments:
        - The winner had to beat more opponents
        - This category contributed more sign-up money

"""

# %% Checking rank distributions
"""
As of reason 3. we want a system where each category gets a weight and based on that weight a proportion of the total budget is assigned.
As of reason 4. we want this weight to increase with the number of participants; i.e. we want a weight per participant where the total weight of a category is just the sum of its participant's weights
As of reason 1. we want this weight to be higher for higher ranked players.

One idea is to have the pariticpant weight depend inversely on the amount of players that have this rank in the overall population. We investigate:
"""
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
fig.write_html("./histogram.html")
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
    .with_columns((pl.col("participants") * pl.col("weight")).alias("weight_per_category"))
    .with_columns(
        (pl.col("weight_per_category") / pl.col("weight_per_category").sum()).alias("normalized_weight")
    )
    .with_columns(
        (pl.col("normalized_weight") * 2500).alias("price_money")
    )
)

dfdijlevallei_weighted.write_csv("dijlevallei_26_calculated.csv")
dfdijlevallei_weighted


# %%
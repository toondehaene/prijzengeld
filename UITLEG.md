# How the Prize Money is Calculated

This document explains the logic behind the prize money distribution for the tournament. The goal is to create a system that is fair, transparent, and rewarding for all participants while respecting the club's budget.

The calculation is based on **four main principles**:

| Principle | Why? |
| :--- | :--- |
| **1. Higher Ranks Earn More** | Better players have invested more time and effort to reach their level. Rewarding high performance promotes growth in the sport. |
| **2. Equal Budget for Men & Women** | Approximately 50% of the population is male/female. We allocate exactly half the total budget to men's categories and half to women's categories. |
| **3. Fixed Total Budget** | The club sets a maximum amount (e.g., €2500) to ensure the tournament does not run a deficit. |
| **4. Participation Matters** | Categories with more players contribute more signup fees and require winning more matches, so they deserve a larger share of the prize pool. |

---

## The Calculation Steps

### Step 1: Determine "Rarity" of Each Rank
We look at the total population of badminton players to see how common or rare each rank is.
- **Common ranks** (many players) get a lower base weight.
- **Rare ranks** (few players) get a higher base weight.

We use a mathematical formula (logarithmic scaling) to ensure that while top ranks get more, the difference isn't absurdly huge. This reflects the exponential difficulty of climbing the ranks.

| Rank Example | Frequency in Population | Base Weight (Difficulty Score) |
| :--- | :--- | :--- |
| **Rank 12 (Beginner)** | Very Common (e.g., 20%) | Low (e.g., 1.5) |
| **Rank 1 (Elite)** | Very Rare (e.g., 0.5%) | High (e.g., 5.3) |

### Step 2: Count Participants
For the specific tournament, we count how many people signed up for each category.

| Category | Rank | Participants | Base Weight | Total Category Score |
| :--- | :--- | :--- | :--- | :--- |
| Men's Singles | 7 | 10 players | 3.0 | 10 × 3.0 = **30.0** |
| Men's Singles | 1 | 8 players | 5.3 | 8 × 5.3 = **42.4** |

*Notice that even with fewer players, the Rank 1 category gets a higher score because the rank is much "heavier" (harder to achieve).*

### Step 3: Split Budget by Gender
We take the total budget (e.g., €2500) and split it strictly in half:
- **€1250** for Male categories (MS, MD, Mixed-Men)
- **€1250** for Female categories (WS, WD, Mixed-Women)

### Step 4: Allocate Money Share
We look at the "Total Category Score" calculated in Step 2.
- If the **Men's Singles Rank 1** has a score of **42.4**...
- And the **Total Score of ALL Male Categories** combined is **424**...
- Then that category gets **10%** (42.4 / 424) of the male budget (€1250).
- Prize Money = 10% × €1250 = **€125**.

### Step 5: Handling Mixed Doubles
Mixed doubles is special because it involves both men and women.
- The male half of the pair draws from the **Male Budget**.
- The female half of the pair draws from the **Female Budget**.
- These two amounts are combined to form the total prize money for the Mixed Doubles category.

### Step 6: Rounding
Finally, we round the amounts to nice, whole numbers to make payouts easier.

---

## Summary Diagram

```mermaid
graph TD
    A[Total Budget €2500] -->|Split 50/50| B(Male Budget €1250)
    A -->|Split 50/50| C(Female Budget €1250)
    
    B --> D{Distribute based on:\n1. Number of Players\n2. Rank Rarity}
    C --> E{Distribute based on:\n1. Number of Players\n2. Rank Rarity}
    
    D --> F[Men's Singles Prize]
    D --> G[Men's Doubles Prize]
    D --> H[Mixed Doubles (Male Share)]
    
    E --> I[Women's Singles Prize]
    E --> J[Women's Doubles Prize]
    E --> K[Mixed Doubles (Female Share)]
    
    H & K --> L[Total Mixed Doubles Prize]
```

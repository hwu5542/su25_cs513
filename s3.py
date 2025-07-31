import pandas as pd
import numpy as np
from pathlib import Path
import os

ROOT_FOLDER = "NYPL-menus"
# "NYPL-menus-cleaned"

OUTPUT_FOLDER = "NYPL-menus-cleaned"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

OUTPUT_FILE = []

MENU = 1
MENU_PAGE = 3
MENU_ITEM = 2
DISH = 0

dataset = []
OUTPUT_FILE = []

print(f"Loading datasets from {ROOT_FOLDER}...")
for filename in sorted(Path(ROOT_FOLDER).iterdir()):
    if filename.name.endswith(".csv"):
        print(f"Loading {filename.name}...")
        OUTPUT_FILE.append(
            filename.name.replace(".csv", "_fixed.csv").replace(
                "_fixed_fixed", "_fixed"
            )
        )
    if filename.name.endswith(".csv"):
        dataset.append(pd.read_csv(filename, na_values=[""]))
print("Datasets loaded.\n")

print("output files:")
print(OUTPUT_FILE)

# IC 2: Date Outliner in Menu

# Extract first 4 digits of call_number (if not null)
dataset[MENU]["call_prefix"] = dataset[MENU]["call_number"].str[:4]

# Extract first 4 digits of date (if not null)
dataset[MENU]["date_prefix"] = dataset[MENU]["date"].str[:4]

# Check constraint: call_prefix == date_year when both exist
ic2_violations = dataset[MENU][
    dataset[MENU]["call_number"].notna()
    & dataset[MENU]["date"].notna()
    & dataset[MENU]["call_prefix"].str.isnumeric()
    & (
        dataset[MENU]["date"].str.match(r"[^1]+")
        | dataset[MENU]["date"].str.match(r"[1][^89]+")
    )
    & (dataset[MENU]["call_prefix"] != dataset[MENU]["date_prefix"])
]

print(f"Before Cleaning Applied: {len(ic2_violations)}")
dataset[MENU].loc[ic2_violations.index][
    ["id", "call_number", "date", "call_prefix", "date_prefix"]
]


# IC 2: Date Outliner in Menu Cleaning
dataset[MENU].loc[ic2_violations.index, "date"] = (
    dataset[MENU].loc[ic2_violations.index, "call_prefix"]
    + dataset[MENU].loc[ic2_violations.index, "date"].str[4:]
)

print(f"After Cleaning Applied: {len(ic2_violations)}")
dataset[MENU].loc[ic2_violations.index][
    ["id", "call_number", "date", "call_prefix", "date_prefix"]
]

# IC 3: Date Blank with call number year in Menu

# Extract first 4 digits of call_number (if not null)
dataset[MENU]["call_prefix"] = dataset[MENU]["call_number"].str[:4]

# Extract first 4 digits of date (if not null)
dataset[MENU]["date_prefix"] = dataset[MENU]["date"].str[:4]

# Check constraint: date should not be blank when call_prefix is numeric
ic3_violations = dataset[MENU][
    dataset[MENU]["call_number"].notna()
    & dataset[MENU]["date"].isna()
    & dataset[MENU]["call_prefix"].str.isnumeric()
]

print(f"Violations found: {len(ic3_violations)}")
ic3_violations[["id", "call_number", "date", "call_prefix", "date_prefix"]].head(20)

# IC 3: Date Blank with call number year in Menu Cleaning
dataset[MENU].loc[ic3_violations.index, "date"] = (
    dataset[MENU].loc[ic3_violations.index, "call_prefix"] + "-01-01"
)

print(f"After Cleaning Applied: {len(ic3_violations)}")
dataset[MENU].loc[ic3_violations.index][
    ["id", "call_number", "date", "call_prefix", "date_prefix"]
]

# IC 4: Date Blank with no date info in call number in Menu

# Extract first 4 digits of call_number (if not null)
dataset[MENU]["call_prefix"] = dataset[MENU]["call_number"].str[:4]

# Extract first 4 digits of date (if not null)
dataset[MENU]["date_prefix"] = dataset[MENU]["date"].str[:4]

# Check constraint: date should not be blank when call_prefix is numeric
ic4_violations = dataset[MENU][
    dataset[MENU]["call_number"].notna()
    & dataset[MENU]["date"].isna()
    & (
        (dataset[MENU]["call_prefix"] == "Zand")
        | (dataset[MENU]["call_prefix"] == "Soet")
        | (dataset[MENU]["call_prefix"] == "soet")
        | (dataset[MENU]["call_prefix"] == "Bara")
        | (dataset[MENU]["call_prefix"] == "_wot")
    )
]

print(f"Violations found: {len(ic4_violations)}")
dataset[MENU].loc[ic4_violations.index][
    ["id", "call_number", "date", "call_prefix", "date_prefix"]
].head(20)


# IC 4: Date Blank with no date info in call number in Menu Cleaning
dataset[MENU]["date"] = dataset[MENU]["date"].ffill()
# .interpolate(method='nearest')

print(f"After Cleaning Applied: {len(ic4_violations)}")
dataset[MENU].loc[ic4_violations.index][
    ["id", "call_number", "date", "call_prefix", "date_prefix"]
]

# # IC 5: Date range outsite of 1890-1970 in Menu
# ic5_violations = dataset[MENU][
#     dataset[MENU]["date"].notna() &
#     (dataset[MENU]["date"].str[:4].astype(int) < 1890) |
#     (dataset[MENU]["date"].str[:4].astype(int) > 1970)
# ]["id"]

# print(f"Violations found: {len(ic5_violations)}")
# print(f"Menu dataset size: {len(dataset[MENU])}")
# print(f"MenuPage dataset size: {len(dataset[MENU_PAGE])}")
# print(f"MenuItem dataset size: {len(dataset[MENU_ITEM])}")
# dataset[MENU].loc[ic5_violations.index]

# # IC 5: Date range outsite of 1890-1970 in Menu Cleaning
# # dataset[MENU] = dataset[MENU][
# #     ~dataset[MENU].isin(ic5_violations)
# # ]
# dataset[MENU] = dataset[MENU][~dataset[MENU]['id'].isin(ic5_violations)]

# # Cant remove yet, due to unlinked items
# # dataset[MENU_PAGE] = dataset[MENU_PAGE][~dataset[MENU_PAGE]['menu_id'].isin(ic5_violations)]
# # dataset[MENU_ITEM] = dataset[MENU_ITEM][~dataset[MENU_ITEM]['menu_page_id'].isin(dataset[MENU_PAGE]['id'])]

# print(f"After Cleaning Applied: {len(ic5_violations)}")
# print(f"Menu dataset size: {len(dataset[MENU])}")
# print(f"MenuPage dataset size: {len(dataset[MENU_PAGE])}")
# print(f"MenuItem dataset size: {len(dataset[MENU_ITEM])}")

# # IC 5: Clean up (remove dishes that no longer appear in any menu items)
# print(f"Dish dataset size: {len(dataset[DISH])}")

# print("Cleaning up Dish dataset...")
# active_dish_ids = dataset[MENU_ITEM]['dish_id'].unique()
# dataset[DISH] = dataset[DISH][
#     dataset[DISH]['id'].isin(active_dish_ids)
# ]

# print(f"Dish dataset size: {len(dataset[DISH])}")

# IC 6: Date blank in Dish with Dependency on Menu

# Extract first 4 digits of date (if not null)
dataset[MENU]["date_prefix"] = dataset[MENU]["date"].str[:4].astype("int64")

dish_appearances = (
    dataset[MENU_ITEM][["id", "dish_id", "menu_page_id"]]
    .merge(
        dataset[MENU_PAGE][["id", "menu_id"]],
        left_on="menu_page_id",
        right_on="id",
        suffixes=("", "_page"),
    )
    .merge(dataset[MENU], left_on="menu_id", right_on="id")
    .groupby("dish_id")["date_prefix"]
    .agg(["min", "max"])
    .reset_index()
    .rename(columns={"min": "calc_first", "max": "calc_last"})
    .astype({"calc_first": "int64", "calc_last": "int64"})
)

dishes = dataset[DISH].merge(
    dish_appearances, left_on="id", right_on="dish_id", how="left"
)

ic6_violations_6_first = dishes[
    (
        dishes["calc_first"].notna()
        & (
            (dishes["first_appeared"].isna())
            | (dishes["first_appeared"] == 0)
            | (dishes["first_appeared"] == 1)
            | (
                dishes["calc_first"].notna()
                & (dishes["first_appeared"] > dishes["calc_first"])
            )
        )
    )
]

ic6_violations_6_last = dishes[
    (dishes["calc_last"].notna())
    & (
        (dishes["last_appeared"].isna())
        | (dishes["last_appeared"] == 0)
        | (dishes["last_appeared"] == 2928)
        | (
            dishes["calc_last"].notna()
            & (dishes["last_appeared"] < dishes["calc_last"])
        )
    )
]

print(f"Violations found: {len(ic6_violations_6_first) + len(ic6_violations_6_last)}")
dishes.loc[ic6_violations_6_first.index][
    ["id", "name", "first_appeared", "last_appeared", "calc_first", "calc_last"]
]

# IC 6: Date blank in Dish with Dependency on Menu Cleaning
dataset[DISH].loc[ic6_violations_6_first.index, "first_appeared"] = dishes.loc[
    ic6_violations_6_first.index, "calc_first"
]

dataset[DISH].loc[ic6_violations_6_last.index, "last_appeared"] = dishes.loc[
    ic6_violations_6_last.index, "calc_last"
]

dataset[DISH]["first_appeared"] = dataset[DISH]["first_appeared"].ffill()
dataset[DISH]["last_appeared"] = dataset[DISH]["last_appeared"].ffill()

print(f"After Cleaning Applied: {len(ic6_violations_6_first)}")
dataset[DISH].loc[ic6_violations_6_first.index][
    ["id", "first_appeared", "last_appeared"]
]

# IC 7: Date Zero in Dish with no dependencies on Menu
ic7_violations_1 = dataset[DISH][
    (dataset[DISH]["first_appeared"] == 0) | (dataset[DISH]["last_appeared"] == 0)
]

ic7_violations_2 = dataset[MENU_ITEM][
    dataset[MENU_ITEM]["dish_id"].isin(dataset[DISH].loc[ic7_violations_1.index, "id"])
]

ic7_violations_3 = dataset[MENU_PAGE][
    dataset[MENU_PAGE]["id"].isin(ic7_violations_2["menu_page_id"])
]

ic7_violations_4 = dataset[MENU][dataset[MENU]["id"].isin(ic7_violations_3["menu_id"])]

ic7_violations_first = dataset[DISH][
    (dataset[DISH]["first_appeared"] == 0) | (dataset[DISH]["first_appeared"] == 1)
]

ic7_violations_last = dataset[DISH][dataset[DISH]["last_appeared"] == 0]

print(f"Violations found: {len(ic7_violations_1)}")
dataset[DISH].loc[ic7_violations_1.index][["id", "first_appeared", "last_appeared"]]

# dataset[MENU_ITEM].loc[ic7_violations_2.index]
# dataset[MENU_PAGE].loc[ic7_violations_3.index]
# dataset[MENU].loc[ic7_violations_4.index]


# IC 7: Date Zero in Dish with no dependencies on Menu Cleaning
dataset[DISH].loc[ic7_violations_first.index, "first_appeared"] = (
    dataset[DISH].loc[ic7_violations_first.index, "first_appeared"].replace(0, np.nan)
)
dataset[DISH].loc[ic7_violations_last.index, "last_appeared"] = (
    dataset[DISH].loc[ic7_violations_last.index, "last_appeared"].replace(0, np.nan)
)

dataset[DISH]["first_appeared"] = dataset[DISH]["first_appeared"].ffill()
dataset[DISH]["last_appeared"] = dataset[DISH]["last_appeared"].ffill()

print(f"After Cleaning Applied: {len(ic7_violations_1)}")
dataset[DISH].loc[ic7_violations_1.index][["id", "first_appeared", "last_appeared"]]

# IC 8: Temporal consistency in Dish
ic8_violations = dataset[DISH][
    dataset[DISH]["first_appeared"] > dataset[DISH]["last_appeared"]
]

print(f"Violations found: {len(ic8_violations)}")
ic8_violations.head(10)

# IC 8: Temporal consistency in Dish cleaning
dataset[DISH].loc[ic8_violations.index, "last_appeared"] = dataset[DISH].loc[
    ic8_violations.index, "first_appeared"
]

print(f"After Cleaning Applied: {len(ic8_violations)}")
dataset[DISH].loc[ic8_violations.index]

# IC 9: Date range outsite of 1880-2000 in Dish
ic9_violations = dataset[DISH][
    dataset[DISH]["first_appeared"].notna()
    & dataset[DISH]["last_appeared"].notna()
    & (
        (dataset[DISH]["first_appeared"] > 2000)
        | (dataset[DISH]["last_appeared"] < 1880)
    )
]
print(f"Violations found: {len(ic9_violations)}")
dataset[DISH].loc[ic9_violations.index][
    ["id", "name", "first_appeared", "last_appeared"]
].head(10)

# IC 9: Date range outsite of 1880-2000 in Dish Cleaning
dataset[DISH] = dataset[DISH][~dataset[DISH]["id"].isin(ic9_violations["id"])]
print(f"After Cleaning Applied: {len(ic9_violations)}")

print(dataset[DISH]["first_appeared"].agg(["min", "max"]))

print(dataset[DISH]["last_appeared"].agg(["min", "max"]))

# IC 10: Blank lowest_price and highest_price in Dish
ic10_violations_1 = dataset[DISH][
    dataset[DISH]["lowest_price"].isna() & dataset[DISH]["highest_price"].isna()
]
print(f"Violations found: {len(ic10_violations_1)}")
dataset[DISH].loc[ic10_violations_1.index][
    ["id", "name", "lowest_price", "highest_price"]
].head(10)

# IC 10: Blank lowest_price and highest_price in Dish with Dependency on Menu Item
menu_item_price = (
    dataset[MENU_ITEM][["id", "dish_id", "price"]]
    .groupby("dish_id")["price"]
    .agg(["min", "max"])
    .reset_index()
    .rename(columns={"min": "calc_lowest", "max": "calc_highest"})
)

dataset[DISH] = dataset[DISH].merge(
    menu_item_price, left_on="id", right_on="dish_id", how="left"
)

ic10_violations_2 = dataset[DISH][
    (dataset[DISH]["lowest_price"].isna() | dataset[DISH]["lowest_price"].isna())
    & (dataset[DISH]["calc_lowest"].notna() | dataset[DISH]["calc_highest"].notna())
]

print(f"Violations found: {len(ic10_violations_2)}")
dataset[DISH].loc[ic10_violations_2.index]

# IC 10: Blank lowest_price and highest_price in Dish with No price info in Menu Item
ic10_violations_3 = dataset[DISH][
    dataset[DISH]["lowest_price"].isna()
    & dataset[DISH]["highest_price"].isna()
    & dataset[DISH]["calc_lowest"].isna()
    & dataset[DISH]["calc_highest"].isna()
]

print(f"Violations found: {len(ic10_violations_3)}")
dataset[DISH].loc[ic10_violations_3.index]

# IC 10: Blank lowest_price and highest_price in Dish with Dependency on Menu Item Cleaning
dataset[DISH].loc[ic10_violations_2.index, "lowest_price"] = dataset[DISH].loc[
    ic10_violations_2.index, "calc_lowest"
]
dataset[DISH].loc[ic10_violations_2.index, "highest_price"] = dataset[DISH].loc[
    ic10_violations_2.index, "calc_highest"
]

print(f"After Cleaning Applied: {len(ic10_violations_2)}")
dataset[DISH].loc[ic10_violations_2.index][
    ["id", "name", "lowest_price", "highest_price"]
].head(10)

# IC 10: Blank lowest_price and highest_price in Dish with No price info in Menu Item Cleaning
print(f"Before Cleaning Applied Dish dataset size: {len(dataset[DISH])}")
dataset[DISH] = dataset[DISH].drop(ic10_violations_3.index, errors="ignore")

print(f"After Cleaning Applied: {len(ic10_violations_3)}")
print(f"Dish dataset size: {len(dataset[DISH])}")

# IC 11: Missing or Null Place Values in Menu
ic11_violations = dataset[MENU][
    dataset[MENU]["place"].isna() | (dataset[MENU]["place"].str.strip() == "")
]

print(f"IC 11 Violations (missing/blank place): {len(ic11_violations)}")
dataset[MENU].loc[ic11_violations.index][["id", "place"]].head()

# Fix for IC 11: Replace missing/blank 'place' with "Unknown"
dataset[MENU]["place"] = dataset[MENU]["place"].fillna("Unknown")
dataset[MENU]["place"] = dataset[MENU]["place"].apply(
    lambda x: "Unknown" if str(x).strip() == "" else x
)

ic11_violations_after = dataset[MENU][
    dataset[MENU]["place"].isna() | (dataset[MENU]["place"].str.strip() == "")
]

print(f"IC 11 Violations After Cleaning: {len(ic11_violations_after)}")
dataset[MENU].loc[ic11_violations.index][["id", "place"]].head()

# IC 12: Place values that are overly specific or not cleanly grouped
valid_groups = [
    "United States",
    "Italy",
    "France",
    "Canada",
    "England",
    "Japan",
    "Germany",
    "China",
    "Austria",
    "Bahamas",
    "Hungary",
    "Cuba",
    "Switzerland",
    "Shipboard",
    "Trainboard",
    "Unknown",
    "Other",
]

ic12_violations = dataset[MENU][~dataset[MENU]["place"].isin(valid_groups)]

print(f"IC 12 Violations (uncategorized place values): {len(ic12_violations)}")
dataset[MENU].loc[ic12_violations.index][["id", "place"]].head()

import re


def categorize_place(place):
    if pd.isnull(place):
        return "Unknown"

    place = str(place).upper().strip()
    place = re.sub(r"[\[\];]", "", place)

    # 1. Unknown or ambiguous
    if place in ["", "UNKNOWN", "?", "Unknown"]:
        return "Unknown"

    # 2. Match by U.S. state abbreviation
    us_states = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VA",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
        "FLA.",
        "N.C.",
        "S.C.",
        "R.I.",
        "MASS",
        "OHIO",
        "PA.",
        "TEXAS",
        "TENN.",
        "MICH",
    ]
    if any(
        f", {state}" in place
        or place.endswith(f" {state}")
        or place.endswith(f"{state}")
        for state in us_states
    ):
        return "United States"

    # 3. Match common U.S. cities
    us_city_terms = [
        "NEW YORK",
        "NYC",
        "ST.AUGUSTINE",
        "TAMPA",
        "CINCINNATI",
        "LOS ANGELES",
        "CHICAGO",
        "[NY]",
        "NY",
        "D.C",
        "SAN FRANCISCO",
    ]
    if any(city in place for city in us_city_terms):
        return "United States"

    # 4. Street addresses (NYC indicator)
    if any(
        term in place
        for term in [
            "ST.",
            "STREET",
            "AVENUE",
            "MADISON",
            "COLUMBUS",
            "PARK AVE",
            "LEXINGTON",
            "5TH AVE",
            "BROADWAY",
            "Park",
        ]
    ):
        return "United States"

    # 5. Known U.S. landmarks (NY hotels/restaurants)
    if any(
        name in place
        for name in ["WALDORF", "DELMONICO", "PLAZA", "GRAMERCY", "SONOMA", "VENTURA"]
    ):
        return "United States"

    # 6. Shipboard patterns
    if any(
        term in place
        for term in [
            "R.M.S.",
            "RMS",
            "S.S.",
            "SS ",
            "STEAMER",
            "DAMPFER",
            "AN BORD DER",
            "ON BOARD",
            "EN ROUTE",
            "AT SEA",
            "SCHNELLDAMPFER",
            "KAISER",
            "KONIGIN",
            "ROUTES",
            "ABOARD",
            "STEAMSHIP",
            "ROUTE",
            "SS",
            "SEA",
            "USMS",
        ]
    ):
        return "Shipboard"

    # 7. Trainboard patterns
    if any(
        term in place for term in ["DINING CAR", "SOUTHERN PACIFIC", "PULLMAN", "CAR"]
    ):
        return "Trainboard"

    # 8. Country-level terms
    if "FRANCE" in place or "PARIS" in place:
        return "France"
    if "GERMANY" in place or "HAMBURG" in place or "BREMEN" in place:
        return "Germany"
    if "CANADA" in place or "ONTARIO" in place or "TORONTO" in place:
        return "Canada"
    if "ENGLAND" in place or "LONDON" in place:
        return "England"
    if "ITALY" in place or "ROME" in place or "FLORENCE" in place:
        return "Italy"
    if "JAPAN" in place or "TOKYO" in place or "YOKOHAMA" in place:
        return "Japan"
    if "CHINA" in place or "HONG KONG" in place or "SHANGHAI" in place:
        return "China"
    if "BAHAMAS" in place or "BERMUDA" in place:
        return "Bahamas"
    if "HAVANA" in place:
        return "Cuba"
    if "BUDAPEST" in place:
        return "Hungary"
    if "ZERMATT" in place or "SWITZERLAND" in place:
        return "Switzerland"
    if "VIENNA" in place or "AUSTRIA" in place:
        return "Austria"

    if any(
        name in place
        for name in ["Hotel", "HOTEL", "INN", "CLUB", "HOUSE", "Maison", "Lounge"]
    ):
        return "Hotel (Unknown Country)"

    # 9. Catch-all
    return "Other"


# Apply place categorization function
dataset[MENU]["cleaned_place"] = dataset[MENU]["place"].apply(categorize_place)
# Recheck IC 12 violations
ic12_violations_after = dataset[MENU][
    ~dataset[MENU]["cleaned_place"].isin(valid_groups)
]

print(f"IC 12 Violations After Cleaning: {len(ic12_violations_after)}")
dataset[MENU].loc[ic12_violations_after.index][["id", "place", "cleaned_place"]].head()

# IC 17: Currency inconsistency in Menu

ic17_violations = dataset[MENU][
    dataset[MENU]["cleaned_place"].notna()
    & dataset[MENU]["cleaned_place"].str.contains("United States")
    & (
        dataset[MENU]["currency"].isna()
        | (dataset[MENU]["currency"].notna() & (dataset[MENU]["currency"] != "Dollars"))
    )
]

print(f"IC 17 Violations (currency inconsistency): {len(ic17_violations)}")

dataset[MENU].loc[ic17_violations.index][["id", "cleaned_place", "currency"]].head()

# IC 17: Place consistency in Menu Cleaning
dataset[MENU].loc[ic17_violations.index, "currency"] = "Dollars"

print(f"After Cleaning Applied: {len(ic17_violations)}")

dataset[MENU].loc[ic17_violations.index][["id", "cleaned_place", "currency"]].head()

# IC 1: find outliners in the price of dishes
# Filter Dollar menus and join with menu items
ic_1_1 = (
    dataset[MENU_ITEM][["id", "price", "menu_page_id"]]
    .merge(
        dataset[MENU_PAGE][["id", "menu_id"]],
        left_on="menu_page_id",
        right_on="id",
        how="left",
    )
    .merge(
        dataset[MENU][["id", "currency"]], left_on="menu_id", right_on="id", how="left"
    )
)

ic_1_1 = ic_1_1[(ic_1_1["currency"] == "Dollars")]

# Calculate percentiles
ic_1_2 = ic_1_1["price"].dropna()
percentiles = {
    "p90": np.percentile(ic_1_2, 90),
    "p95": np.percentile(ic_1_2, 95),
    "p999": np.percentile(ic_1_2, 99.9),
}

ic_1_3_1 = ic_1_1[(ic_1_1["price"] >= percentiles["p999"]) | ic_1_1["price"].isna()]

# Identify outliers (above 99.9 percentile) and empty prices
ic_1_3 = ic_1_1[
    (ic_1_1["price"] >= percentiles["p999"])
    | ic_1_1["price"].isna()
    | (ic_1_1["price"] <= 0)
]

print("Price Percentiles (Dollar items):")
print(f"90th: ${percentiles['p90']:.2f}")
print(f"95th: ${percentiles['p95']:.2f}")
print(f"999th: ${percentiles['p999']:.2f}")

print(f"\nFound {len(ic_1_3)} potential outliers:")
print(f"\nFound {len(ic_1_3_1)} items with price >= 99.9 percentile:")
print(ic_1_3[["id", "price", "menu_id"]].head(10))


# IC 1: find outliners in the price of dishes Cleaning
print(f"Before Cleaning Applied: {len(dataset[MENU_ITEM])}")
len_before = len(dataset[MENU_ITEM])
dataset[MENU_ITEM] = dataset[MENU_ITEM].drop(ic_1_3.index, errors="ignore")
print(f"After Cleaning Applied: {len(dataset[MENU_ITEM])}")
print(
    f"Removed {len_before - len(dataset[MENU_ITEM])} items from MenuItem dataset due to price outliers."
)

# IC 18: the average price of dishes every 20 years from 1880 to 2000

# IC 18.1: Dollar currency in Menu
ic_18_1 = dataset[MENU][dataset[MENU]["currency"] == "Dollars"]
# IC 18.2: Connect dishes to their menu appearances
ic_18_2 = (
    dataset[MENU_ITEM][["dish_id", "price", "menu_page_id"]]
    .merge(dataset[MENU_PAGE][["id", "menu_id"]], left_on="menu_page_id", right_on="id")
    .merge(ic_18_1, left_on="menu_id", right_on="id")
    .merge(
        dataset[DISH][["id", "first_appeared", "last_appeared"]],
        left_on="dish_id",
        right_on="id",
    )
)

# IC 18.3:  Create 20-year periods
periods = [(year, year + 19) for year in range(1880, 2000, 20)]
periods[5] = (1980, 2000)

# IC 18.4: Calculate average price for each period
avg_prices = []
for start, end in periods:
    # IC 18.5: Find dishes active during each period
    IC_18_5 = ic_18_2[
        (ic_18_2["first_appeared"] <= end) & (ic_18_2["last_appeared"] >= start)
    ]

    IC_18_5["price"].head()

    # Calculate all required statistics
    avg_price = IC_18_5["price"].mean()
    median_price = IC_18_5["price"].median()
    standard_deviation = IC_18_5["price"].std()
    max_price = IC_18_5["price"].max()
    min_price = IC_18_5["price"].min()

    avg_prices.append(
        {
            "period": f"{start}-{end}",
            "avg_price": round(avg_price, 2),
            "median_price": round(median_price, 2),
            "std_dev": round(standard_deviation, 2),
            "max_price": round(max_price, 2),
            "min_price": round(min_price, 2),
            "num_dishes": len(IC_18_5["dish_id"].unique()),
            "num_menus": len(IC_18_5["menu_id"].unique()),
        }
    )

print("IC 18: Average price of dishes every 20 years from 1880 to 2000")
# convert avg_prices to DataFrame
ic_18_df = pd.DataFrame(avg_prices)
ic_18_df.head(6)

# Export the cleaned dataset
dataset[MENU].drop(columns=["date_prefix", "call_prefix"], inplace=True)
dataset[DISH].drop(columns=["calc_lowest", "calc_highest"], inplace=True)

for i in range(len(dataset)):
    dataset[i].to_csv(Path(OUTPUT_FOLDER) / OUTPUT_FILE[i], index=False)

# IC 13:  DINNER/LUNCH/TIFFIN/BREAKFAST in different language or descriptions

ic13_violations = dataset[MENU][
    dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains(
        "FRUHSTUCK|MITTAGESSEN|ABENDESSEN|DINER|DEJEUNER|NOON|(\bTEA\b)|MIDDAY|EVENING",
        regex=True,
    )
    | dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains(
        "FRUHSTUCK|MITTAGESSEN|ABENDESSEN|DINER|DEJEUNER|NOON|(\bTEA\b)|MIDDAY|EVENING",
        regex=True,
    )
]

print(f"Violations found: {len(ic13_violations)}")
dataset[MENU].loc[ic13_violations.index][["event", "occasion"]]


## IC 13:  DINNER/LUNCH/TIFFIN/BREAKFAST in different language or descriptions. Cleaning.

# @BEGIN openrefine_basic_clean_cluster
# @PARAM OUTPUT_FOLDER
# @IN dataset[MENU]  @AS Menu_fixed  @URI file:{OUTPUT_FOLDER}/Menu_fixed.csv
# @OUT dataset[MENU]  @AS Menu_fixed_openrefined  @URI file:/Menu_fixed_ic13_ORCluster.csv
# @END openrefine_basic_clean_cluster

input_filename = "Menu_fixed_ic13_ORCluster.csv"
dataset[MENU] = pd.read_csv(input_filename, na_values=[""])

# IC 13: cleaning results from openrefine

print(f"Before Cleaning Applied Dish dataset size: {dataset[MENU].shape}")

ic13_violations_after = dataset[MENU][
    dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains(
        "FRUHSTUCK|MITTAGESSEN|ABENDESSEN|DINER|DEJEUNER|NOON|(\bTEA\b)|MIDDAY|EVENING|MIDDAG",
        regex=True,
    )
    | dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains(
        "FRUHSTUCK|MITTAGESSEN|ABENDESSEN|DINER|DEJEUNER|NOON|(\bTEA\b)|MIDDAY|EVENING|MIDDAG",
        regex=True,
    )
]

dataset[MENU]["meal_type"] = ""
## Create a new column meal_type that isolates out type of meal
breakfast_filter = dataset[MENU]["occasion"].fillna("na").str.upper().str.contains(
    "BREAKFAST"
) | dataset[MENU]["event"].fillna("na").str.upper().str.contains("BREAKFAST")
dataset[MENU].loc[breakfast_filter, "meal_type"] = (
    dataset[MENU].loc[breakfast_filter, "meal_type"] + "B"
)

lunch_filter = dataset[MENU]["occasion"].fillna("na").str.upper().str.contains(
    "LUNCH"
) | dataset[MENU]["event"].fillna("").str.upper().str.contains("LUNCH")
dataset[MENU].loc[lunch_filter, "meal_type"] = (
    dataset[MENU].loc[lunch_filter, "meal_type"] + "L"
)

tiffin_filter = dataset[MENU]["occasion"].fillna("na").str.upper().str.contains(
    "TIFFIN"
) | dataset[MENU]["event"].fillna("").str.upper().str.contains("TIFFIN")
dataset[MENU].loc[tiffin_filter, "meal_type"] = (
    dataset[MENU].loc[tiffin_filter, "meal_type"] + "T"
)

dinner_filter = dataset[MENU]["occasion"].fillna("na").str.upper().str.contains(
    "SUPPER|DINNER"
) | dataset[MENU]["event"].fillna("").str.upper().str.contains("SUPPER|DINNER")
dataset[MENU].loc[dinner_filter, "meal_type"] = (
    dataset[MENU].loc[dinner_filter, "meal_type"] + "D"
)


print(f"IC 13 Violations After Cleaning: {len(ic13_violations_after)}")
print(f"Dish dataset size: {dataset[MENU].shape}")


# IC 14: event and occasion field contains pure information on menu.
# e.g WINE XXX LIST/ROOM SERVICE
# those are not helpful to identify what event there is

ic14_violations = dataset[MENU][
    dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains("[A-z]+\sLIST", regex=True)
    | dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains("[A-z]+\sLIST", regex=True)
    | dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains("^ROOM SERVICE$", regex=True)
    | dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains("^ROOM SERVICE$", regex=True)
]


print(f"Violations found: {len(ic14_violations)}")
dataset[MENU].loc[ic14_violations.index][["event", "occasion"]]


# IC 14: event and occasion field contains pure information on menu. Cleaning
# e.g WINE XXX LIST/ROOM SERVICE
# those are not helpful to identify what event there is

event_toclean_filter = dataset[MENU]["event"].fillna("na").str.upper().str.contains(
    "[A-z]+\sLIST", regex=True
) | dataset[MENU]["event"].fillna("na").str.upper().str.contains(
    "^ROOM SERVICE$", regex=True
)
dataset[MENU].loc[event_toclean_filter, "event"] = np.nan

occasion_toclean_filter = dataset[MENU]["occasion"].fillna(
    "na"
).str.upper().str.contains("[A-z]+\sLIST", regex=True) | dataset[MENU][
    "occasion"
].fillna(
    "na"
).str.upper().str.contains(
    "^ROOM SERVICE$", regex=True
)
dataset[MENU].loc[occasion_toclean_filter, "occasion"] = np.nan


ic14_violations_after = dataset[MENU][
    dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains("[A-z]+\sLIST", regex=True)
    | dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains("[A-z]+\sLIST", regex=True)
    | dataset[MENU]["event"]
    .fillna("na")
    .str.upper()
    .str.contains("^ROOM SERVICE$", regex=True)
    | dataset[MENU]["occasion"]
    .fillna("na")
    .str.upper()
    .str.contains("^ROOM SERVICE$", regex=True)
]

print(f"IC 14 Violations After Cleaning: {len(ic14_violations_after)}")
print(f"Dish dataset size: {dataset[MENU].shape}")
dataset[MENU].loc[ic14_violations_after.index, ["occasion", "event"]].head()


# IC 15: A DAILY MENU that was NOT used for a special occastion/holiday. It should be exlcuded from our analysis.

ic15_violations = dataset[MENU][
    (
        dataset[MENU]["event"].fillna("na").str.upper().str.contains("DAILY|REGULAR")
        | dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("DAILY|REGULAR")
    )
    & (~dataset[MENU]["event"].fillna("na").str.contains("HOLIDAY|FOR|TO|OF"))
    & (~dataset[MENU]["occasion"].fillna("na").str.contains("HOLIDAY|FOR|TO|OF"))
]


print(f"Violations found: {len(ic15_violations)}")
dataset[MENU].loc[ic15_violations.index][["event", "occasion"]]


# IC 15: A DAILY MENU that was NOT used for a special occastion/holiday. It should be exlcuded from our analysis. Cleaning

## Remove those daily events from occastion_event column
print(f"Before Cleaning Applied Dish dataset size: {dataset[MENU].shape}")


## Create a new column special_occasion with both occation and event information combined
## Use Occasioin first, if occasion is NaN use event. Because event if more noisy.
dataset[MENU]["special_occasion"] = np.where(
    dataset[MENU]["occasion"].isna(), dataset[MENU]["event"], dataset[MENU]["occasion"]
)

dataset[MENU]["special_occasion"] = (
    dataset[MENU]["special_occasion"]
    .fillna("")
    .str.replace("BREAKFAST|DINNER|SUPPER|LUNCHEON|LUNCH|TIFFIN", "", regex=True)
)

## below is some trivial cleaning. removal of MENU, A LA CARTE, OR, & /

dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    "MENU|MEAL|(A LA CARTE)", "", regex=True
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    " OR ", ""
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    "&", ""
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    "/", ""
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    "-", " "
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.replace(
    "^AND$", "", regex=True
)
dataset[MENU]["special_occasion"] = dataset[MENU]["special_occasion"].str.strip()


ic15_violations_withOR = dataset[MENU][
    (
        dataset[MENU]["event"].fillna("na").str.upper().str.contains("DAILY|REGULAR")
        | dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("DAILY|REGULAR")
    )
    & (~dataset[MENU]["event"].fillna("na").str.contains("HOLIDAY|FOR|TO|OF"))
    & (~dataset[MENU]["occasion"].fillna("na").str.contains("HOLIDAY|FOR|TO|OF"))
]

dataset[MENU].loc[ic15_violations_withOR.index, "special_occasion"] = ""

ic15_violations_after = dataset[MENU][
    (
        dataset[MENU]["special_occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("DAILY|REGULAR")
        & (
            ~dataset[MENU]["special_occasion"]
            .fillna("na")
            .str.contains("HOLIDAY|FOR|TO|OF")
        )
    )
]

print(f"IC 15 Violations After Cleaning: {len(ic15_violations_after)}")
print(f"Dish dataset size: {dataset[MENU].shape}")
dataset[MENU].loc[
    ic15_violations.index, ["special_occasion", "occasion", "event"]
].head()

# IC 16: A WEEKDAY MENU that was NOT used for a special occastion/holiday. It should be exlcuded from our analysis.

ic16_violations = dataset[MENU][
    (
        dataset[MENU]["event"]
        .fillna("na")
        .str.upper()
        .str.contains("MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY")
        | dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY")
    )
    & (
        ~dataset[MENU]["event"]
        .fillna("na")
        .str.upper()
        .str.contains("THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR")
    )
    & (
        ~dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR")
    )
]


print(f"Violations found: {len(ic16_violations)}")
dataset[MENU].loc[ic16_violations.index][["event", "occasion"]]

# IC 16: A WEEKDAY MENU that was NOT used for a special occastion/holiday. It should be exlcuded from our analysis. Cleaning

## Remove those weekday menus events from occastion_event column
print(f"Before Cleaning Applied Dish dataset size: {dataset[MENU].shape}")

ic16_violations_withOR = dataset[MENU][
    (
        dataset[MENU]["event"]
        .fillna("na")
        .str.upper()
        .str.contains("MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY")
        | dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY")
    )
    & (
        ~dataset[MENU]["event"]
        .fillna("na")
        .str.upper()
        .str.contains("THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR")
    )
    & (
        ~dataset[MENU]["occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR")
    )
]


dataset[MENU].loc[ic16_violations_withOR.index, "special_occasion"] = ""

ic16_violations_after = dataset[MENU][
    (
        dataset[MENU]["special_occasion"]
        .fillna("na")
        .str.upper()
        .str.contains("MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY")
        & (
            ~dataset[MENU]["special_occasion"]
            .fillna("na")
            .str.contains("THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR")
        )
    )
]

print(f"IC 16 Violations After Cleaning: {len(ic16_violations_after)}")
print(f"Dish dataset size: {dataset[MENU].shape}")
dataset[MENU].loc[
    ic16_violations.index, ["special_occasion", "occasion", "event"]
].head()

dataset[MENU].to_csv(
    Path(OUTPUT_FOLDER) / ("Menu_fixed_clean_occasion.csv"), index=False
)

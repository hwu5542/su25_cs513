import pandas as pd
import numpy as np
from pathlib import Path
import os
import re

# @BEGIN main
# @PARAM ROOT_FOLDER
# @PARAM OUTPUT_FOLDER
# @IN input_files @URI file:{ROOT_FOLDER}/*.csv
# @OUT cleaned_files @URI file:{OUTPUT_FOLDER}/*_fixed.csv
# @OUT analysis_results @URI file:{OUTPUT_FOLDER}/Menu_fixed_clean_occasion.csv


def main(ROOT_FOLDER="NYPL-menus", OUTPUT_FOLDER="NYPL-menus-cleaned"):

    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    OUTPUT_FILE = []

    MENU = 1
    MENU_PAGE = 3
    MENU_ITEM = 2
    DISH = 0

    dataset = []
    OUTPUT_FILE = []

    # @BEGIN load_datasets
    # @PARAM ROOT_FOLDER
    # @IN input_files @URI file:{ROOT_FOLDER}/*.csv
    # @OUT dataset @AS loaded_data
    print(f"Loading datasets from {ROOT_FOLDER}...")
    for filename in sorted(Path(ROOT_FOLDER).iterdir()):
        if filename.name.endswith(".csv"):
            print(f"Loading {filename.name}...")
            OUTPUT_FILE.append(
                filename.name.replace(".csv", "_fixed.csv").replace(
                    "_fixed_fixed", "_fixed"
                )
            )
            dataset.append(pd.read_csv(filename, na_values=[""]))
    print("Datasets loaded.\n")
    print("output files:")
    print(OUTPUT_FILE)
    # @END load_datasets

    # @BEGIN clean_menu_dates
    # @IN dataset @AS loaded_data
    # @OUT dataset @AS date_cleaned_data

    # IC 2: Date Outliner in Menu
    dataset[MENU]["call_prefix"] = dataset[MENU]["call_number"].str[:4]
    dataset[MENU]["date_prefix"] = dataset[MENU]["date"].str[:4]

    ic2_violations = dataset[MENU][
        dataset[MENU]["call_number"].notna()
        & dataset[MENU]["date"].notna()
        & (dataset[MENU]["call_prefix"] != dataset[MENU]["date_prefix"])
    ]
    dataset[MENU].loc[ic2_violations.index, "date"] = (
        dataset[MENU].loc[ic2_violations.index, "call_prefix"]
        + dataset[MENU].loc[ic2_violations.index, "date"].str[4:]
    )

    # IC 3: Date Blank with call number year in Menu
    ic3_violations = dataset[MENU][
        dataset[MENU]["call_number"].notna()
        & dataset[MENU]["date"].isna()
        & dataset[MENU]["call_prefix"].str.isnumeric()
    ]
    dataset[MENU].loc[ic3_violations.index, "date"] = (
        dataset[MENU].loc[ic3_violations.index, "call_prefix"] + "-01-01"
    )

    # IC 4: Date Blank with no date info in call number in Menu
    ic4_violations = dataset[MENU][
        dataset[MENU]["call_number"].notna()
        & dataset[MENU]["date"].isna()
        & (dataset[MENU]["call_prefix"].isin(["Zand", "Soet", "soet", "Bara", "_wot"]))
    ]
    dataset[MENU]["date"] = dataset[MENU]["date"].ffill()
    # @END clean_menu_dates

    # @BEGIN clean_dish_dates
    # @IN dataset @AS date_cleaned_data
    # @OUT dataset @AS dish_date_cleaned_data

    # IC 6: Date blank in Dish with Dependency on Menu
    dish_appearances = (
        dataset[MENU_ITEM][["id", "dish_id", "menu_page_id"]]
        .merge(
            dataset[MENU_PAGE][["id", "menu_id"]], left_on="menu_page_id", right_on="id"
        )
        .merge(dataset[MENU], left_on="menu_id", right_on="id")
        .groupby("dish_id")["date_prefix"]
        .agg(["min", "max"])
        .rename(columns={"min": "calc_first", "max": "calc_last"})
    )

    dishes = dataset[DISH].merge(
        dish_appearances, left_on="id", right_on="dish_id", how="left"
    )

    ic6_violations_6_first = dishes[
        dishes["calc_first"].notna() & (dishes["first_appeared"].isna())
    ]
    ic6_violations_6_last = dishes[
        dishes["calc_last"].notna() & (dishes["last_appeared"].isna())
    ]

    dataset[DISH].loc[ic6_violations_6_first.index, "first_appeared"] = dishes.loc[
        ic6_violations_6_first.index, "calc_first"
    ]
    dataset[DISH].loc[ic6_violations_6_last.index, "last_appeared"] = dishes.loc[
        ic6_violations_6_last.index, "calc_last"
    ]
    dataset[DISH]["first_appeared"] = dataset[DISH]["first_appeared"].ffill()
    dataset[DISH]["last_appeared"] = dataset[DISH]["last_appeared"].ffill()

    # IC 8: Temporal consistency in Dish
    ic8_violations = dataset[DISH][
        dataset[DISH]["first_appeared"] > dataset[DISH]["last_appeared"]
    ]
    dataset[DISH].loc[ic8_violations.index, "last_appeared"] = dataset[DISH].loc[
        ic8_violations.index, "first_appeared"
    ]

    # IC 9: Date range outside of 1880-2000 in Dish
    ic9_violations = dataset[DISH][
        (dataset[DISH]["first_appeared"] > 2000)
        | (dataset[DISH]["last_appeared"] < 1880)
    ]
    dataset[DISH] = dataset[DISH][~dataset[DISH]["id"].isin(ic9_violations["id"])]
    # @END clean_dish_dates

    # @BEGIN clean_prices
    # @IN dataset @AS dish_date_cleaned_data
    # @OUT dataset @AS price_cleaned_data

    # IC 10: Blank lowest_price and highest_price in Dish
    menu_item_price = (
        dataset[MENU_ITEM][["id", "dish_id", "price"]]
        .groupby("dish_id")["price"]
        .agg(["min", "max"])
        .rename(columns={"min": "calc_lowest", "max": "calc_highest"})
    )

    dataset[DISH] = dataset[DISH].merge(
        menu_item_price, left_on="id", right_on="dish_id", how="left"
    )

    ic10_violations_2 = dataset[DISH][
        (dataset[DISH]["lowest_price"].isna() | dataset[DISH]["highest_price"].isna())
        & (dataset[DISH]["calc_lowest"].notna() | dataset[DISH]["calc_highest"].notna())
    ]

    dataset[DISH].loc[ic10_violations_2.index, "lowest_price"] = dataset[DISH].loc[
        ic10_violations_2.index, "calc_lowest"
    ]
    dataset[DISH].loc[ic10_violations_2.index, "highest_price"] = dataset[DISH].loc[
        ic10_violations_2.index, "calc_highest"
    ]

    # IC 1: find outliers in the price of dishes
    ic_1_1 = (
        dataset[MENU_ITEM][["id", "price", "menu_page_id"]]
        .merge(
            dataset[MENU_PAGE][["id", "menu_id"]], left_on="menu_page_id", right_on="id"
        )
        .merge(dataset[MENU][["id", "currency"]], left_on="menu_id", right_on="id")
    )
    ic_1_1 = ic_1_1[(ic_1_1["currency"] == "Dollars")]
    ic_1_3 = ic_1_1[(ic_1_1["price"] >= np.percentile(ic_1_1["price"].dropna(), 99.9))]
    dataset[MENU_ITEM] = dataset[MENU_ITEM].drop(ic_1_3.index, errors="ignore")
    # @END clean_prices

    # @BEGIN clean_places
    # @IN dataset @AS price_cleaned_data
    # @OUT dataset @AS place_cleaned_data

    # IC 11: Missing or Null Place Values in Menu
    dataset[MENU]["place"] = dataset[MENU]["place"].fillna("Unknown")
    dataset[MENU]["place"] = dataset[MENU]["place"].apply(
        lambda x: "Unknown" if str(x).strip() == "" else x
    )

    # IC 12: Place values that are overly specific
    def categorize_place(place):
        if pd.isnull(place):
            return "Unknown"
        place = str(place).upper().strip()
        place = re.sub(r"[\[\];]", "", place)

        if place in ["", "UNKNOWN", "?", "Unknown"]:
            return "Unknown"
        # ... (rest of categorization logic)
        return "Other"

    dataset[MENU]["cleaned_place"] = dataset[MENU]["place"].apply(categorize_place)

    # IC 17: Currency inconsistency in Menu
    ic17_violations = dataset[MENU][
        dataset[MENU]["cleaned_place"].str.contains("United States")
        & (dataset[MENU]["currency"] != "Dollars")
    ]
    dataset[MENU].loc[ic17_violations.index, "currency"] = "Dollars"
    # @END clean_places

    # @BEGIN clean_occasions
    # @IN dataset @AS place_cleaned_data
    # @OUT dataset @AS occasion_cleaned_data

    # IC 13-16: Clean occasions and events
    dataset[MENU]["meal_type"] = ""
    breakfast_filter = (
        dataset[MENU]["occasion"].fillna("na").str.upper().str.contains("BREAKFAST")
    )
    dataset[MENU].loc[breakfast_filter, "meal_type"] = "B"

    # ... (other meal type categorizations)

    dataset[MENU]["special_occasion"] = np.where(
        dataset[MENU]["occasion"].isna(),
        dataset[MENU]["event"],
        dataset[MENU]["occasion"],
    )
    dataset[MENU]["special_occasion"] = (
        dataset[MENU]["special_occasion"]
        .fillna("")
        .str.replace("BREAKFAST|DINNER|SUPPER|LUNCHEON|LUNCH|TIFFIN", "", regex=True)
    )
    # @END clean_occasions

    # @BEGIN export_results
    # @PARAM OUTPUT_FOLDER
    # @IN dataset @AS occasion_cleaned_data
    # @OUT cleaned_files @URI file:{OUTPUT_FOLDER}/*_fixed.csv
    # @OUT analysis_results @URI file:{OUTPUT_FOLDER}/Menu_fixed_clean_occasion.csv
    dataset[MENU].drop(columns=["date_prefix", "call_prefix"], inplace=True)
    dataset[DISH].drop(columns=["calc_lowest", "calc_highest"], inplace=True)

    for i in range(len(dataset)):
        dataset[i].to_csv(Path(OUTPUT_FOLDER) / OUTPUT_FILE[i], index=False)

    dataset[MENU].to_csv(
        Path(OUTPUT_FOLDER) / "Menu_fixed_clean_occasion.csv", index=False
    )
    # @END export_results


# @END main

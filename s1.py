import pandas as pd
from pandas_profiling import ProfileReport

# import numpy as np

ROOT_FOLDER = "NYPL-menus"


class s1:

    def __init__(self):
        self.menu = pd.read_csv(ROOT_FOLDER + "/Menu.csv", na_values=[""])
        self.menu_page = pd.read_csv(ROOT_FOLDER + "/MenuPage.csv", na_values=[""])
        self.menu_item = pd.read_csv(ROOT_FOLDER + "/MenuItem.csv", na_values=[""])
        self.dish = pd.read_csv(ROOT_FOLDER + "/Dish.csv", na_values=[""])

    def loadDataset(self, dataset_name):
        if dataset_name == "dish info":
            self.dish.info()
        elif dataset_name == "page info":
            self.menu_page.info()
        elif dataset_name == "item":
            print(self.menu_item.isna().sum())
        elif dataset_name == "dish":
            self.dish.describe(include="all")
        elif dataset_name == "report":
            dish_profile = ProfileReport(self.dish, title="Dish Profiling Report")
            dish_profile.to_file("dish_profile.html")
            menu_profile = ProfileReport(self.menu, title="Menu Profiling Report")
            menu_profile.to_file("menu_profile.html")
        else:
            raise ValueError("Unknown dataset name: {}".format(dataset_name))


if __name__ == "__main__":
    dataset = s1()

    print("S1 Align U1 with Dataset Description")
    print("Enter a request (or 'quit' to exit):")

    while True:
        user_input = input("> ")

        if user_input.lower() == "quit" or user_input.lower() == "exit":
            print("Exiting program...")
            break

        if not user_input:
            print("Please enter a valid string or 'quit' to exit")
            continue

        try:
            dataset.loadDataset(user_input)
        except ValueError as e:
            print(f"Error: {e}")
            continue

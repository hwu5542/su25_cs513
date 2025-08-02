# @BEGIN clean_prices # @DESC clean dish prices
# @IN dish_lowest_price
# @IN dish_highest_price
# @IN menu_dish_price
# @OUT dish_lowest_price_cleaned
# @OUT dish_highest_price_cleaned


# @BEGIN calculate_dish_price_from_menu # @DESC calculate dish highest lowest price from menus dish price information 
# @IN dish_lowest_price
# @IN dish_highest_price
# @IN menu_dish_price
# @OUT dish_lowest_price_caled
# @OUT dish_highest_price_caled
# @END calculate_dish_price_from_menu

# @BEGIN drop_missing_dish_prices # @DESC drop those dishes with missing price and could not be calculated 
# @IN dish_lowest_price_caled
# @IN dish_highest_price_caled
# @OUT dish_lowest_price_cleaned
# @OUT dish_highest_price_cleaned
# @END drop_missing_dish_prices


# @END clean_prices
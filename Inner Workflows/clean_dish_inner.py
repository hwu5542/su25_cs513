# @BEGIN clean_dish_dates # @DESC clean the date field in dish dataset
# @IN dish_first_appear
# @IN dish_last_appear
# @IN menu_date_cleaned
# @OUT dish_first_appear_cleaned
# @OUT dish_last_appear_cleaned

# @BEGIN calculate_nan_from_menu # @DESC caculate missing first_appear and last_appear from Menu dates 
# @IN dish_first_appear
# @IN dish_last_appear
# @IN menu_date_cleaned
# @OUT dish_first_appear_caled
# @OUT dish_last_appear_caled
# @END calculate_nan_from_menu

# @BEGIN removed_Temporal_inconsistencies # @DESC set those with first_appear later than last_appear to have last_appear floored to first_appear 
# @IN dish_first_appear_caled
# @IN dish_last_appear_caled
# @OUT dish_first_appear_consistent
# @OUT dish_last_appear_consistent
# @END removed_Temporal_inconsistencies


# @BEGIN remove_dish_outside_range # @DESC Remove those dish outsite of 1880-2000 in Dish 
# @IN dish_first_appear_consistent
# @IN dish_last_appear_consistent
# @OUT dish_first_appear_cleaned
# @OUT dish_last_appear_cleaned
# @END remove_dish_outside_range

# @END clean_dish_dates

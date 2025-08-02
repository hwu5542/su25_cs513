# @BEGIN clean_menu_dates # @DESC Clean Date outliers and fillna Date in Menu dataset
# @IN date
# @OUT menu_date_cleaned


# @BEGIN clean_menu_date_outlier # @DESC Clean misformated year
# @IN date
# @OUT date_clean1
# @END clean_menu_date_outlier



# @BEGIN fill_in_blank_dates # @DESC fill in blank dates with call_number info other wise forward fill
# @IN date_clean1
# @OUT menu_date_cleaned
# @END fill_in_blank_dates

# @END clean_menu_dates
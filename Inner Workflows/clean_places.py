# @BEGIN clean_places # @DESC clean the places to get geolocation of menus
# @IN menu_place
# @OUT menu_place_cleaned

# @BEGIN fillna_places_with_unknown
# @PARAM expression: menu.place.fillna('Unknown')
# @IN menu_place
# @OUT menu_place_no_na
# @END fillna_places_with_unknown

# @BEGIN detailed_catagorization_places # @ parse the place information into unified format
# @IN menu_place_no_na
# @OUT menu_place_cleaned
# @END detailed_catagorization_places

# @END clean_places


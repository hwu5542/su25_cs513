# @BEGIN clean_occasions # @DESC Clean occasion and event field into special_occation and meal_type
# @PARAM use open refine for basic cleaning, term unification and clustering and then Python for Filtering
# @IN occasion
# @IN event
# @OUT special_occasion
# @OUT meal_type

def function():
    # @BEGIN openrefine_basic_clean_cluster # @DESC Open Refine Operations in a sperate Workflow Diagram
    # @PARAM OUTPUT_FOLDER
    # @PARAM A seriies of OpenRefine Cleaning and Cluster operations
    # @IN occasion  @URI file:{OUTPUT_FOLDER}/Menu_fixed.csv['occasion']
    # @IN event   @URI file:{OUTPUT_FOLDER}/Menu_fixed.csv['event']
    # @OUT occasion_ORclean  @URI file:/Menu_fixed_ic13_ORCluster.csv['occasion']
    # @OUT event_ORclean  @URI file:/Menu_fixed_ic13_ORCluster.csv['occasion']
    # @END openrefine_basic_clean_cluster
    pass
def function2():
    # @BEGIN create_meal_type # @DESC Strip out meal_type such as DINNER/BREAKFAST/LUNCH from occasion and events
    # @PARAM create new field meal_type with following mapping: B:Breakfast, L: Lunch/Luncheon, D: Dinner/Supper, T:Tiffin/Tea
    # @IN occasion_ORclean
    # @IN event_ORclean  
    # @OUT meal_type
    # @END create_meal_type
    pass

def function3():
    # @BEGIN Remove non occasion information # @DESC Remove those description like WINE LIST/ROOM SERVICE from occastion
    # @PARAM expression:value.replace(/[A-z]+\sLIST/,np.nan)
    # @IN occasion_ORclean
    # @IN event_ORclean  
    # @OUT occasion_clean2
    # @OUT event_clean2
    # @END Remove_non_occasion_information
    pass

def function4():
    # @BEGIN filter_out_nonspecial_events # @DESC Filter out non special event/occastions
    # @PARAM filter out occasion and events by: value.str.contains('DAILY|REGULAR') but not value.str.contains('HOLIDAY|FOR|TO|OF')
    # @IN occasion_clean2
    # @IN event_clean2  
    # @OUT occasion_filter1
    # @OUT event_filter1
    # @END filter_out_nonspecial_events
    pass

def function5():
    # @BEGIN filter_out_nonholiday_weekdays_weekends_menus # @DESC Filter out non special event/occastions and weekend/weekday menu
    # @PARAM filter out occasion and events by: value.str.contains('MONDAY|TUESDAY|WEDNESDAY|THURSDAY|FRIDAY|SATURDAY|SUNDAY') but not value.str.contains('THANKSGIVING|CHRISTMAS|EASTER|OF|TO|FOR')
    # @IN occasion_filter1
    # @IN event_filter1  
    # @OUT occasion_filter2
    # @OUT event_filter2  
    # @END filter_out_nonholiday_weekdays_weekends_menus
    pass

def function6():
    # @BEGIN Merge_occasion_event_to_special_occasion # @DESC Merge occasion_clean2 and event_clean2 into special_occasio
    # @PARAM expression: strip out any meal_type in the field: value.str.str.replace("BREAKFAST|DINNER|SUPPER|LUNCHEON|LUNCH|TIFFIN","")
    # @PARAM Merge occasion and event into special_occasion with occasion as main and backup Nans with event
    # @IN occasion_filter2
    # @IN event_filter2  
    # @OUT special_occasion
    # @END Merge_occasion_event_to_special_occasion
    pass
# @END clean_occasions




import reporting.database_reports as rep 

def main():

    print("==== Basic Stats ====")
    rep.print_basic_stats()
    print("==== Additional Stats ====")
    rep.print_additional_stats()
    print("==== Unit Breakdown ====")
    rep.print_unit_breakdown()
    print("==== Alloy Conversion Failures ====")
    # rep.print_alloy_conversion_failure_counts()
    

if __name__ == "__main__":
    main()
    print("Done!")

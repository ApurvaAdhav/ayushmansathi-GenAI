from app.records import load_records, search, count_by, get_by_id

def main():
    records = load_records()

    while True:
        print("\n========== AYUSHMANSATHI ==========")
        print("1. View All Records")
        print("2. Search Records")
        print("3. Count Records")
        print("4. Get Record by ID")
        print("0. Exit")

        choice = input("\nEnter your choice: ").strip()

        # View all records
        if choice == "1":
            print("\n========== ALL RECORDS ==========")

            for record in records:
                print("\nID:", record["id"])
                print("Topic:", record["rule_topic"])
                print("Rule:", record["rule_text"])
                print("Applies To:", record["applies_to"])

        # Search records by keyword
        elif choice == "2":
            keyword = input("\nEnter a topic or keyword to search: ").strip()

            if keyword:
                results = search(records, keyword)

                if results:
                    print("\n========== SEARCH RESULTS ==========")

                    for record in results:
                        print("\nID:", record["id"])
                        print("Topic:", record["rule_topic"])
                        print("Rule:", record["rule_text"])
                        print("Applies To:", record["applies_to"])
                else:
                    print("\nNo matching records found.")
            else:
                print("\nPlease enter a keyword.")

        # Count records by category
        elif choice == "3":
            general_topics = [
                "Amount",
                "Eligibility",
                "Beneficiary Identification",
                "Pre-authorisation",
                "Discharge Against Advice",
                "Death in Hospital",
                "Referral",
                "Unspecified Packages"
            ]

            general_count = sum(
                count_by(records, topic) for topic in general_topics
            )

            print("\n========== RECORD COUNTS ==========")
            print("General Rules:", general_count)
            print("Exclusions:", count_by(records, "Exclusion"))
            print("FAQs:", count_by(records, "FAQ"))
            print("Total Records:", len(records))

        # Get record by ID
        elif choice == "4":
            record_id = input("\nEnter record ID: ").strip()

            if record_id.isdigit():
                result = get_by_id(records, int(record_id))

                if result:
                    print("\n========== RECORD DETAILS ==========")
                    print("\nID:", result["id"])
                    print("Topic:", result["rule_topic"])
                    print("Rule:", result["rule_text"])
                    print("Applies To:", result["applies_to"])
                    print("Document:", result["document_title"])
                    print("Reference:", result["page_or_section"])
                    print("Source URL:", result["source_url"])
                else:
                    print("\nRecord not found.")
            else:
                print("\nPlease enter a valid record ID.")

        # Exit
        elif choice == "0":
            print("\nThank you for using AyushmanSathi!")
            break

        else:
            print("\nInvalid choice. Please try again.")


if __name__ == "__main__":
    main()
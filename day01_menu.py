
# AyushmanSathi - AI Healthcare Assistant
# Day 01: Menu-Driven Program

while True:

    print("\n" + "-" * 45)
    print("Welcome to AyushmanSathi")
    print("1. About AyushmanSathi")
    print("2. Sample Healthcare Questions")
    print("3. Healthcare Rule Check")
    print("0. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "":
        print("Input cannot be empty. Please try again.")
        continue

    elif choice == "1":

        print("\nAbout AyushmanSathi")
        print("AyushmanSathi is an AI-powered healthcare information assistant. It aims to make reliable healthcare information accessible to everyone.")
        print("It provides information on various health topics, symptoms, and preventive measures based on trusted sources like WHO and MoHFW.")
        print("Our goal is to empower patients, caregivers, and the general public with accurate healthcare knowledge.")

    elif choice == "2":

        print("\nSample Healthcare Questions:")
        print("1. What is a balanced diet?")
        print("2. What are the common symptoms of fever?")
        print("3. Why is regular exercise important?")
        print("4. How can I improve my sleep?")

    elif choice == "3":

        age = input("\nEnter your age: ")

        if age == "":
            print("Age cannot be empty. Please try again.")
            continue

        elif age.isdigit():

            age = int(age)

            if age < 1 or age > 120:
                print("Please enter an age between 1 and 120.")

            elif age < 18:
                print("You belong to the under-18 age group.")

            elif age <= 60:
                print("You belong to the adult age group.")

            else:
                print("You belong to the senior age group.")

        else:
            print("Invalid age. Please enter a numeric value.")

    elif choice == "0":

        print("\nThank you for using AyushmanSathi!")
        break

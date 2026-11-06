
# AyushmanSathi - AI Healthcare Assistant
# Day 01: Project Introduction

# Project Details
product = "AyushmanSathi - AI Healthcare Assistant"
target_users = "Patients, Caregivers, and General Public"
problem = "Difficulty accessing reliable healthcare information"
data_source = "WHO, MoHFW, and trusted healthcare resources"

# Display Project Card
print("\n========== AYUSHMANSATHI PROJECT CARD ==========")

print(f"Product      : {product}")
print(f"Target Users : {target_users}")
print(f"Problem      : {problem}")
print(f"Data Sources : {data_source}")

print("=" * 52)

# Get User Information
name = input("\nEnter your name: ")

if name == "":
    print("Please enter your name.")

question = input("Enter your healthcare question: ")

if question == "":
    print("Please enter your healthcare question.")

# Display User Information
print("\n========== USER INFORMATION ==========")

print(f"Welcome to AyushmanSathi, {name}!")
print(f"Your Question: {question}")

print("\nThank you for using AyushmanSathi!")
print("=" * 52)

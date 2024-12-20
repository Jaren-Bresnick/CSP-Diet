import google.generativeai as genai
import os
from dotenv import load_dotenv #for the .env folder with the api key 
load_dotenv() #protect sensitive info
import pandas as pd
import numpy as np

#combined meal dataset with recipes and nutritional info on ingredients
combined_file = "meals_with_combined_nutrition_LLM_data.xlsx"
meals_df = pd.read_excel(combined_file)

#make the health score column
if "Health Score" not in meals_df.columns:
    def calculate_health_score(row):
        penalties = (
            row.get("sugars_100g", 0) * 2 +
            row.get("saturated-fat_100g", 0) * 2 +
            row.get("sodium_100g", 0) * 2
        )
        # print("sugars: " + str(row.get("sugars_100g", 0)))
        # print("fat: " + str(row.get("saturated-fat_100g", 0)))
        # print("sodium: " + str(row.get("sodium_100g", 0)))

        rewards = (
            row.get("fiber_100g", 0) * 2 +
            row.get("proteins_100g", 0) * 2 +
            row.get("vitamin-c_100g", 0) * 2
        )
        return rewards - penalties

    meals_df["Health Score"] = meals_df.apply(calculate_health_score, axis=1)

    #normalize the health score
    min_score = meals_df["Health Score"].min()
    max_score = meals_df["Health Score"].max()
    meals_df["Health Score"] = (meals_df["Health Score"] - min_score) / (max_score - min_score) * 100

# User-defined meal preferences
total_calories = float(input("Enter your total daily calorie target: "))
total_protein = float(input("Enter your total daily protein target (g): "))
total_fat = float(input("Enter your total daily fat target (g): "))
total_carbs = float(input("Enter your total daily carbohydrate target (g): "))
num_breakfast = int(input("Enter the number of breakfast items: "))
num_lunch = int(input("Enter the number of lunch items: "))
num_dinner = int(input("Enter the number of dinner items: "))

#Allergies
print("Any Allergies?")
#lowercase and comma delimited
allergies = set(input().lower().split(','))

# Define meal targets
meal_targets = {
    "Breakfast": {"calories": total_calories * 0.3 / num_breakfast, "protein": total_protein * 0.3 / num_breakfast, "fat": total_fat * 0.3 / num_breakfast, "carbs": total_carbs * 0.3 / num_breakfast},
    "Lunch": {"calories": total_calories * 0.4 / num_lunch, "protein": total_protein * 0.4 / num_lunch, "fat": total_fat * 0.4 / num_lunch, "carbs": total_carbs * 0.4 / num_lunch},
    "Dinner": {"calories": total_calories * 0.3 / num_dinner, "protein": total_protein * 0.3 / num_dinner, "fat": total_fat * 0.3 / num_dinner, "carbs": total_carbs * 0.3 / num_dinner},
}

# Save original input targets
original_targets = {
    "calories": total_calories,
    "protein": total_protein,
    "fat": total_fat,
    "carbs": total_carbs,
}

# Realistic serving sizes
serving_fractions = [1, 0.5, 0.33, 0.25]

# Function to optimize single food per meal
def optimize_food_for_meal(meal_targets, excluded_foods, allergies):
    best_food = None
    best_score = float("inf")
    best_serving = None

    for index, food in meals_df.iterrows():
        if food["Meal Name"] in excluded_foods:
            continue
        
        # Check for allergies
        ingredients = str(food["Ingredients (MealDB)"]).lower()
        if any(allergen in ingredients for allergen in allergies):
            continue

        for fraction in serving_fractions:
            quantity = fraction * 100  # Scale to 100g servings
            total_calories = quantity * food["energy-kcal_100g"] / 100
            total_protein = quantity * food["proteins_100g"] / 100
            total_fat = quantity * food["fat_100g"] / 100
            total_carbs = quantity * food["carbohydrates_100g"] / 100

            deviation = (
                (total_calories - meal_targets["calories"]) ** 2 +
                (total_protein - meal_targets["protein"]) ** 2 +
                (total_fat - meal_targets["fat"]) ** 2 +
                (total_carbs - meal_targets["carbs"]) ** 2
            )
            score = deviation - food["Health Score"]

            if score < best_score:
                best_score = score
                best_food = food
                best_serving = fraction

    return best_food, best_serving

# Gen AI (LLM)
def gen_AI(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    print(response.text)

# Optimize meals
optimized_meals = {}
excluded_foods = set()
overall_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

for meal_name, targets in meal_targets.items():
    print(f"\nOptimizing {meal_name}...")
    optimized_meals[meal_name] = []
    for _ in range(num_breakfast if meal_name == "Breakfast" else (num_lunch if meal_name == "Lunch" else num_dinner)):
        best_food, best_serving = optimize_food_for_meal(targets, excluded_foods, allergies)
        if best_food is not None:
            total_calories = best_food["energy-kcal_100g"] * best_serving
            total_protein = best_food["proteins_100g"] * best_serving
            total_fat = best_food["fat_100g"] * best_serving
            total_carbs = best_food["carbohydrates_100g"] * best_serving

            # Update overall totals
            overall_totals["calories"] += total_calories
            overall_totals["protein"] += total_protein
            overall_totals["fat"] += total_fat
            overall_totals["carbs"] += total_carbs

            optimized_meals[meal_name].append({
                "food_name": best_food["Meal Name"],
                "serving": best_serving,
                "quantity": best_serving * 100,
                "energy": total_calories,
                "protein": total_protein,
                "fat": total_fat,
                "carbs": total_carbs,
                "ingredients": best_food["Ingredients (MealDB)"]
            })
            excluded_foods.add(best_food["Meal Name"])

# Calculate match percentages using original targets
calories_match = max(0, 100 - abs(overall_totals["calories"] - original_targets["calories"]) / original_targets["calories"] * 100)
protein_match = max(0, 100 - abs(overall_totals["protein"] - original_targets["protein"]) / original_targets["protein"] * 100)
fat_match = max(0, 100 - abs(overall_totals["fat"] - original_targets["fat"]) / original_targets["fat"] * 100)
carbs_match = max(0, 100 - abs(overall_totals["carbs"] - original_targets["carbs"]) / original_targets["carbs"] * 100)

overall_match_percentage = (calories_match + protein_match + fat_match + carbs_match) / 4

if overall_match_percentage < 70:

    prompt = f"""
    
    You are a meal planning assistant. The user's original targets were:
    - Total Calories: {original_targets['calories']} kcal
    - Protein: {original_targets['protein']} g
    - Fat: {original_targets['fat']} g
    - Carbohydrates: {original_targets['carbs']} g
    
    You are required provide them with meal suggestions that accomodates with their constraints.
    
    Give {num_breakfast} meal suggestion for Breakfast.
    Give {num_lunch} meal suggestion for Lunch.
    Give {num_dinner} meal suggestion for Dinner. 
    
    If the meal name appears more than once, then give different suggestions for as many as it appears.
     
    Structure your response in this format:
    " 
    (meal name): 
    Food: <Food Name>
    Ingredients: <List of Ingredients>
    Serving: <Number of Servings>
    Quantity: <Quantity in grams>
    Energy: <Energy in kcal>
    Protein: <Protein in grams>
    Fat: <Fat in grams>
    Carbs: <Carbs in grams>
    "
    
    After you have given a suggest for every meal then calculate and give the overall totals in this format.
    "Overall Totals:
    Calories: <Total Calories in kcal>
    Protein: <Total Protein in grams>
    Fat: <Total Fat in grams>
    Carbs: <Total Carbs in grams>

    

    The match percentage should be calculated by comparing the actual values (e.g., calories, protein, fat, and carbs) with the target values provided by the user. The formula should calculate the percentage difference for each category as follows:

    Match Percentage for each category = (1 - |(Actual Value - Target Value) / Target Value|) * 100

    For each category:
    If the match percentage is below 0%, set it to 0%.
    If the match percentage exceeds 100%, set it to 0%.
    Then calculate the overall match percentage by averaging the match percentages of all categories. Here are the input values:

    Do not show intermediate steps in the output and provide the final result for the overall match percentage.
    Try to keep the overall totals as close to the user's original targets as possible. 
    Make sure the overall match percentage is greater than 70%.

    Your output should only include the instruction given inside the quotations. Keep the response concise.
    """

    print("\nProcessing Gen-AI..")
    print(gen_AI(prompt))

else: 
    # Print results
    for meal_name, foods in optimized_meals.items():
        print(f"\n{meal_name}:")
        for food in foods:
            print(f"  Food: {food['food_name']}")
            print(f"  Ingredients: {food['ingredients']}")
            print(f"  Serving: {food['serving']}x")
            print(f"  Quantity: {food['quantity']:.2f} g")
            print(f"  Energy: {food['energy']:.2f} kcal")
            print(f"  Protein: {food['protein']:.2f} g")
            print(f"  Fat: {food['fat']:.2f} g")
            print(f"  Carbs: {food['carbs']:.2f} g")

    print("\nOverall Totals:")
    print(f"  Calories: {overall_totals['calories']:.2f} kcal")
    print(f"  Protein: {overall_totals['protein']:.2f} g")
    print(f"  Fat: {overall_totals['fat']:.2f} g")
    print(f"  Carbs: {overall_totals['carbs']:.2f} g")


    # # Print the overall match percentage
    # print(f"\nOverall Match Percentage: {overall_match_percentage:.2f}%")









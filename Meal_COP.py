import pandas as pd
import numpy as np

#Load the combined meal dataset
combined_file = "meals_with_combined_nutrition_LLM_data.xlsx"
meals_df = pd.read_excel(combined_file)

def calculate_health_score(row):
    penalties = (
        row.get("sugars_100g", 0) * 2 +
        row.get("saturated-fat_100g", 0) * 3 +
        row.get("sodium_100g", 0) / 1000
    )
    # print(row.get("sugars_100g", 0))
    rewards = (
        row.get("fiber_100g", 0) * 2 +
        row.get("proteins_100g", 0) * 1.5 +
        row.get("potassium_100g", 0)
    )
    return rewards - penalties

#make a health score column for optimization
if "Health Score" not in meals_df.columns:
    meals_df["Health Score"] = meals_df.apply(calculate_health_score, axis=1)
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
print("Any Allergies (write None if none)?")
#lowercase and comma delimited
allergies = set(input().lower().split(','))

#Vitamin Preference
print("Enter a vitamin you prefer (e.g., vitamin-c, vitamin-a):")
pref_vitamin = input().lower()

print(f"Enter your daily target for {pref_vitamin} (mg or IU) (80 is average):")
pref_vitamin_target = float(input())

if pref_vitamin == None:
    pref_vitamin = "vitamin-c"
    pref_vitamin_target = 80


# Define meal targets
meal_targets = {
    "Breakfast": {"calories": total_calories * 0.3 / num_breakfast, "protein": total_protein * 0.3 / num_breakfast, "fat": total_fat * 0.3 / num_breakfast, "carbs": total_carbs * 0.3 / num_breakfast, "vitamins": pref_vitamin_target * 0.3 / num_breakfast},
    "Lunch": {"calories": total_calories * 0.4 / num_lunch, "protein": total_protein * 0.4 / num_lunch, "fat": total_fat * 0.4 / num_lunch, "carbs": total_carbs * 0.4 / num_lunch, "vitamins": pref_vitamin_target * 0.4 / num_lunch},
    "Dinner": {"calories": total_calories * 0.3 / num_dinner, "protein": total_protein * 0.3 / num_dinner, "fat": total_fat * 0.3 / num_dinner, "carbs": total_carbs * 0.3 / num_dinner, "vitamins": pref_vitamin_target * 0.3 / num_dinner},
}

# Save original input targets
original_targets = {
    "calories": total_calories,
    "protein": total_protein,
    "fat": total_fat,
    "carbs": total_carbs, 
    "vitamins": pref_vitamin_target
}

# Realistic serving sizes
serving_fractions = [1, 0.5, 0.33, 0.25]

# Function to optimize single food per meal
def optimize_food_for_meal(meal_targets, excluded_foods, allergies, vitamin):
    best_food = None
    best_score = float("inf")
    best_serving = None

    for index, food in meals_df.iterrows():
        if food["Meal Name"] in excluded_foods:
            continue

        # Check for allergies
        if allergies is not None:
            ingredients = str(food["Ingredients (MealDB)"]).lower()
            if any(allergen in ingredients for allergen in allergies):
                continue

        for fraction in serving_fractions:
            quantity = fraction * 100  # Scale to 100g servings
            total_calories = quantity * food["energy-kcal_100g"] / 100
            total_protein = quantity * food["proteins_100g"] / 100
            total_fat = quantity * food["fat_100g"] / 100
            total_carbs = quantity * food["carbohydrates_100g"] / 100
            total_vitamin = quantity * food.get(vitamin + "_100g", 0) / 100


            deviation = (
                (total_calories - meal_targets["calories"]) ** 2 +
                (total_protein - meal_targets["protein"]) ** 2 +
                (total_fat - meal_targets["fat"]) ** 2 +
                (total_carbs - meal_targets["carbs"]) ** 2 +
                (total_vitamin - meal_targets["vitamins"]) ** 2
            )
            
            score = deviation - food["Health Score"]

            if score < best_score:
                best_score = score
                best_food = food
                best_serving = fraction

    return best_food, best_serving

# Optimize meals
optimized_meals = {}
excluded_foods = set()
overall_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0, "vitamins": 0}

for meal_name, targets in meal_targets.items():
    print(f"\nOptimizing {meal_name}...")
    optimized_meals[meal_name] = []
    for _ in range(num_breakfast if meal_name == "Breakfast" else (num_lunch if meal_name == "Lunch" else num_dinner)):
        best_food, best_serving = optimize_food_for_meal(targets, excluded_foods, allergies, pref_vitamin)
        if best_food is not None:
            total_calories = best_food["energy-kcal_100g"] * best_serving
            total_protein = best_food["proteins_100g"] * best_serving
            total_fat = best_food["fat_100g"] * best_serving
            total_carbs = best_food["carbohydrates_100g"] * best_serving
            total_vitamins = best_food[pref_vitamin + "_100g"] * best_serving

            # Update overall totals
            overall_totals["calories"] += total_calories
            overall_totals["protein"] += total_protein
            overall_totals["fat"] += total_fat
            overall_totals["carbs"] += total_carbs
            overall_totals["vitamins"] += total_vitamins

            optimized_meals[meal_name].append({
                "food_name": best_food["Meal Name"],
                "serving": best_serving,
                "quantity": best_serving * 100,
                "energy": total_calories,
                "protein": total_protein,
                "fat": total_fat,
                "carbs": total_carbs,
                "vitamins": total_vitamins,
                "ingredients": best_food["Ingredients (MealDB)"]
            })
            excluded_foods.add(best_food["Meal Name"])

# Calculate match percentages using original targets
calories_match = max(0, 100 - abs(overall_totals["calories"] - original_targets["calories"]) / original_targets["calories"] * 100)
protein_match = max(0, 100 - abs(overall_totals["protein"] - original_targets["protein"]) / original_targets["protein"] * 100)
fat_match = max(0, 100 - abs(overall_totals["fat"] - original_targets["fat"]) / original_targets["fat"] * 100)
carbs_match = max(0, 100 - abs(overall_totals["carbs"] - original_targets["carbs"]) / original_targets["carbs"] * 100)
vitamins_match = max(0, 100 - abs(overall_totals["vitamins"] - original_targets["vitamins"]) / original_targets["vitamins"] * 100)

overall_match_percentage = (calories_match + protein_match + fat_match + carbs_match + vitamins_match) / 5

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
        print(f"  {pref_vitamin.capitalize()}: {food['vitamins']:.2f} g")

print("\nOverall Totals:")
print(f"  Calories: {overall_totals['calories']:.2f} kcal")
print(f"  Protein: {overall_totals['protein']:.2f} g")
print(f"  Fat: {overall_totals['fat']:.2f} g")
print(f"  Carbs: {overall_totals['carbs']:.2f} g")
print(f"  Vitamins: {overall_totals['vitamins']:.2f} g")


# Print the overall match percentage
print(f"\nOverall Match Percentage: {overall_match_percentage:.2f}%")

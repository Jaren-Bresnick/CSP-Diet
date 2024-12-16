import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv #for the .env folder with the api key
load_dotenv() #protect sensitive info
import os

meals_file = "meals_with_combined_nutrition_LLM_data.xlsx"
meal_df = pd.read_excel(meals_file)

important_columns = [
    "Meal Name", "Ingredients (MealDB)", "energy-kcal_100g",
    "proteins_100g", "fat_100g", "carbohydrates_100g", "sugars_100g", "saturated-fat_100g",
    "sodium_100g", "fiber_100g", "vitamin-c_100g"
]

existing_meal_names = set(meal_df["Meal Name"].dropna().unique())
limited_meal_names = list(existing_meal_names)[-150:]

def gen_ai(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return(response.text)

meal_names_str = ", ".join(limited_meal_names)
prompt = f"""
    Generate 20 unique meal recipes that is not in the following list of meal names: {meal_names_str}
    Generate the list in the following format:
    - Meal Name: <meal name>
    - Ingredients (MealDB): <comma-separated list of ingredients>
    - energy-kcal_100g: <numeric value>
    - proteins_100g: <numeric value>
    - fat_100g: <numeric value>
    - carbohydrates_100g: <numeric value>
    - sugars_100g: <numeric value>
    - saturated-fat_100g: <numeric value>
    - sodium_100g: <numeric value>
    - fiber_100g: <numeric value>
    - vitamin-c_100g: <numeric value>

    Ensure that the nutritional values are realistic for the described meal.
    Ensure no two recipes share the same meal name or ingredients.
"""


meal_data = []

count = 0

print ("Processing Gemini...\n")

generated_response = gen_ai(prompt)
if generated_response:
    meals = generated_response.strip().split("\n\n")
    for meal in meals:
        meal_name = ""
        ingredients = ""
        energy = ""
        proteins = ""
        fat = ""
        carbs = ""
        sugar = ""
        saturated_fat = ""
        sodium = ""
        fiber = ""
        vitamin_c = ""

        for line in meal.split("\n"):
            if line.startswith("- Meal Name:"):
                meal_name = line.split(":")[1].strip()
                print(meal_name)
            if line.startswith("- Ingredients (MealDB)"):
                ingredients = line.split(":")[1].strip()
            if line.startswith("- energy-kcal_100g"):
                energy = line.split(":")[1].strip()
            if line.startswith("- proteins_100g:"):
                proteins = line.split(":")[1].strip()
            if line.startswith("- fat_100g:"):
                fat = line.split(":")[1].strip()
            if line.startswith("- carbohydrates_100g"):
                carbs = line.split(":")[1].strip()
            if line.startswith("- sugars_100g"):
                sugar = line.split(":")[1].strip()
            if line.startswith("- saturated-fat_100g"):
                saturated_fat = line.split(":")[1].strip()
            if line.startswith("- sodium_100g"):
                sodium = line.split(":")[1].strip()
            if line.startswith("- fiber_100g"):
                fiber = line.split(":")[1].strip()
            if line.startswith("- vitamin-c_100g"):
                vitamin_c = line.split(":")[1].strip()

        if (meal_name and ingredients and energy and proteins and fat and carbs and
                sugar and saturated_fat and sodium and fiber and vitamin_c):
            meal_data.append({
                "Meal Name": meal_name,
                "Ingredients (MealDB)": ingredients,
                "energy-kcal_100g": energy,
                "proteins_100g": proteins,
                "fat_100g": fat,
                "carbohydrates_100g": carbs,
                "sugars_100g": sugar,
                "saturated-fat_100g": saturated_fat,
                "sodium_100g": sodium,
                "fiber_100g": fiber,
                "vitamin-c_100g": vitamin_c
            })


new_df = pd.DataFrame(meal_data, columns=important_columns)

updated_df = pd.concat([meal_df, new_df], ignore_index=True)

updated_df.to_excel(meals_file, index=False)

print(f"Appended {len(new_df)} rows. The file now has {len(updated_df)} rows.")


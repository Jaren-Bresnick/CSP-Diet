import os
import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

load_dotenv()

# Load the combined meal dataset with recipes and nutritional info
combined_file = "meals_with_combined_nutrition_data_LLM_data.xlsx"
meals_df = pd.read_excel(combined_file)

# Ensure Health Score column exists
if "Health Score" not in meals_df.columns:
    def calculate_health_score(row):
        penalties = (
            row.get("sugars_100g", 0) * 2 +
            row.get("saturated-fat_100g", 0) * 2 +
            row.get("sodium_100g", 0) * 2
        )
        rewards = (
            row.get("fiber_100g", 0) * 2 +
            row.get("proteins_100g", 0) * 2 +
            row.get("vitamin-c_100g", 0) * 2
        )
        return rewards - penalties

    meals_df["Health Score"] = meals_df.apply(calculate_health_score, axis=1)

    # Normalize the health score
    min_score = meals_df["Health Score"].min()
    max_score = meals_df["Health Score"].max()
    meals_df["Health Score"] = (meals_df["Health Score"] - min_score) / (max_score - min_score) * 100

# Define serving fractions
serving_fractions = [1, 0.5, 0.33, 0.25]

# Preprocess meals data for faster access
foods = meals_df.to_dict('records')
for food in foods:
    food['Ingredients (MealDB)'] = food.get("Ingredients (MealDB)", "").lower()

def optimize_food_for_meal(meal_targets, excluded_foods, allergies):
    best_food = None
    best_score = float("inf")
    best_serving = None

    for food in foods:
        if food["Meal Name"] in excluded_foods:
            continue
        ingredients = food['Ingredients (MealDB)']
        if any(allergen in ingredients for allergen in allergies):
            continue

        for fraction in serving_fractions:
            total_calories = fraction * food.get("energy-kcal_100g", 0)
            total_protein = fraction * food.get("proteins_100g", 0)
            total_fat = fraction * food.get("fat_100g", 0)
            total_carbs = fraction * food.get("carbohydrates_100g", 0)

            deviation = (
                (total_calories - meal_targets["calories"]) ** 2 +
                (total_protein - meal_targets["protein"]) ** 2 +
                (total_fat - meal_targets["fat"]) ** 2 +
                (total_carbs - meal_targets["carbs"]) ** 2
            )
            score = deviation - food.get("Health Score", 0)

            if score < best_score:
                best_food, best_score, best_serving = food, score, fraction

    return best_food, best_serving

def run_meal_planning(total_calories, total_protein, total_fat, total_carbs, 
                      num_breakfast, num_lunch, num_dinner, allergies):
    meal_targets = {
        "Breakfast": {"calories": total_calories * 0.3 / num_breakfast, "protein": total_protein * 0.3 / num_breakfast, "fat": total_fat * 0.3 / num_breakfast, "carbs": total_carbs * 0.3 / num_breakfast},
        "Lunch": {"calories": total_calories * 0.4 / num_lunch, "protein": total_protein * 0.4 / num_lunch, "fat": total_fat * 0.4 / num_lunch, "carbs": total_carbs * 0.4 / num_lunch},
        "Dinner": {"calories": total_calories * 0.3 / num_dinner, "protein": total_protein * 0.3 / num_dinner, "fat": total_fat * 0.3 / num_dinner, "carbs": total_carbs * 0.3 / num_dinner},
    }
    original_targets = {"calories": total_calories, "protein": total_protein, "fat": total_fat, "carbs": total_carbs}

    optimized_meals = {}
    excluded_foods = set()
    overall_totals = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}

    for meal_name, targets in meal_targets.items():
        optimized_meals[meal_name] = []
        times = num_breakfast if meal_name == "Breakfast" else (num_lunch if meal_name == "Lunch" else num_dinner)
        for _ in range(times):
            best_food, best_serving = optimize_food_for_meal(targets, excluded_foods, allergies)
            if best_food is not None:
                overall_totals["calories"] += best_food.get("energy-kcal_100g", 0) * best_serving
                overall_totals["protein"] += best_food.get("proteins_100g", 0) * best_serving
                overall_totals["fat"] += best_food.get("fat_100g", 0) * best_serving
                overall_totals["carbs"] += best_food.get("carbohydrates_100g", 0) * best_serving

                optimized_meals[meal_name].append({"food_name": best_food["Meal Name"], "serving": best_serving})
                excluded_foods.add(best_food["Meal Name"])

    overall_match_percentage = sum(
        max(0, 100 - abs(overall_totals[k] - original_targets[k]) / original_targets[k] * 100)
        for k in overall_totals
    ) / 4

    return overall_match_percentage, optimized_meals

def generate_simulation_params(n, calories_range, protein_range, fat_range, carbs_range,
                               num_breakfast_range, num_lunch_range, num_dinner_range, allergies_list):
    params = []
    for _ in range(n):
        total_calories = random.randint(*calories_range)
        total_protein = random.randint(*protein_range)
        total_fat = random.randint(*fat_range)
        total_carbs = random.randint(*carbs_range)

        num_breakfast = random.randint(*num_breakfast_range)
        num_lunch = random.randint(*num_lunch_range)
        num_dinner = random.randint(*num_dinner_range)

        chosen_allergy = random.choice(allergies_list)
        allergies = {chosen_allergy} if chosen_allergy.strip() else set()

        params.append((total_calories, total_protein, total_fat, total_carbs, 
                      num_breakfast, num_lunch, num_dinner, allergies))
    return params

def main():
    n_simulations = 100000
    calories_range = (1500, 3000)
    protein_range = (50, 200)
    fat_range = (30, 100)
    carbs_range = (150, 400)
    num_breakfast_range = (1, 2)
    num_lunch_range = (1, 2)
    num_dinner_range = (1, 2)
    allergies_list = [
    # Dairy Products
    "milk", "skim milk", "whole milk", "buttermilk", "evaporated milk", "condensed milk", "powdered milk", 
    "cream", "heavy cream", "light cream", "whipped cream", "sour cream", "butter", "ghee", "clarified butter", 
    "yogurt", "greek yogurt", "kefir", "cheese", "cheddar cheese", "mozzarella", "feta", "goat cheese", 
    "sheep cheese", "blue cheese", "brie", "camembert", "ricotta", "cottage cheese", "cream cheese", 
    "mascarpone", "whey", "casein", "lactose", "milk solids", "milk powder", "custard", "milk fat",

    # Eggs
    "eggs", "egg white", "egg yolk", "dried egg powder", "mayonnaise", "aioli", "meringue", "egg wash", "albumen",

    # Peanuts and Tree Nuts
    "peanuts", "peanut butter", "peanut oil", "almonds", "almond butter", "almond milk", "walnuts", "cashews", 
    "cashew butter", "hazelnuts", "pistachios", "pecans", "macadamia nuts", "pine nuts", "praline", 
    "nut butters", "nut oils", "chestnuts", "brazil nuts",

    # Soy and Soy Products
    "soybeans", "soy milk", "soy sauce", "tamari", "miso", "tofu", "tempeh", "edamame", "textured vegetable protein (TVP)", 
    "soy lecithin", "soy protein isolate", "soy flour", "hydrolyzed soy protein", "natto", "soya",

    # Wheat, Gluten, and Grains
    "wheat", "whole wheat flour", "white flour", "durum wheat", "semolina", "spelt", "barley", "rye", 
    "triticale", "farro", "bulgur", "couscous", "malt", "wheat starch", "gluten", "wheat bran", 
    "wheat germ", "oats", "oat flour", "oatmeal", "bread flour", "cake flour", "self-rising flour", "pasta",

    # Fish and Shellfish
    "fish", "salmon", "tuna", "cod", "haddock", "halibut", "mackerel", "sardines", "anchovies", "trout", 
    "snapper", "grouper", "herring", "pollock", "sole", "flounder", "tilapia", "bass", "catfish", "sea bass",
    "shellfish", "shrimp", "prawns", "crab", "lobster", "crayfish", "clams", "mussels", "scallops", "oysters", 
    "cockles", "squid", "octopus", "cuttlefish", "fish sauce", "anchovy paste", "oyster sauce",

    # Seeds and Oils
    "sesame", "tahini", "sesame oil", "mustard", "mustard seeds", "sunflower seeds", "sunflower oil", 
    "pumpkin seeds", "pumpkin seed oil", "poppy seeds", "chia seeds", "flax seeds", "linseed", 
    "hemp seeds", "hemp oil", "cottonseed oil", "rapeseed oil", "canola oil",

    # Fruits and Vegetables
    "apples", "peaches", "apricots", "cherries", "kiwi", "strawberries", "bananas", "avocados", "tomatoes", 
    "bell peppers", "potatoes", "eggplant", "peppers", "mango", "pineapple", "papaya", "melon", "cantaloupe", 
    "watermelon", "citrus", "oranges", "lemons", "limes", "grapefruit", "coconut", "coconut milk", "coconut oil",

    # Legumes and Beans
    "chickpeas", "lentils", "kidney beans", "black beans", "pinto beans", "green peas", "split peas", 
    "lima beans", "fava beans", "navy beans", "cannellini beans", "soybeans", "edamame", "bean sprouts",

    # Flavorings and Condiments
    "honey", "pollen", "garlic", "onions", "shallots", "leeks", "chives", "curry powder", "red curry paste", 
    "green curry paste", "horseradish", "worcestershire sauce", "vinegar", "red wine vinegar", "balsamic vinegar", 
    "hot sauce", "ketchup", "mustard oil", "soybean oil", "teriyaki sauce", "barbecue sauce",

    # Spices and Herbs
    "cumin", "turmeric", "coriander", "cinnamon", "nutmeg", "ginger", "cardamom", "allspice", "paprika", 
    "chili powder", "anise", "fennel seeds", "caraway seeds", "saffron", "thyme", "rosemary", "oregano", 
    "parsley", "cilantro",

    # Additives and Preservatives
    "guar gum", "xanthan gum", "lecithin", "agar agar", "carrageenan", "yeast extract", "MSG (monosodium glutamate)",
    "sodium caseinate", "malt flavoring", "malt extract", "vegimite", "brewer's yeast",

    # Alcohol and Fermented Products
    "beer", "wine", "red wine", "white wine", "sherry", "mirin", "sake", "kombucha", "fermented soy", "kimchi",

    # Miscellaneous
    "truffles", "mushrooms", "seaweed", "nori", "dashi", "gelatin", "lard", "tallow", "shortening", "animal fat", 
    "pork", "beef", "bacon", "chorizo", "gelatin", "collagen", "bone broth", "meat stock", "duck", "lamb", 
    "shellac", "carmine", "egg substitutes", "imitation crab", "processed meat", "artificial sweeteners", 
    "aspartame", "sorbitol", "stevia", "coconut sugar"
]


    results = []
    count = 0  # Initialize count
    for params in generate_simulation_params(
        n_simulations, calories_range, protein_range, fat_range, carbs_range,
        num_breakfast_range, num_lunch_range, num_dinner_range, allergies_list
    ):
        match_percentage, _ = run_meal_planning(*params)
        results.append(match_percentage)
        
        # Increment count and print progress every 100 iterations
        count += 1
        if count % 100 == 0:
            print(f"Completed {count} runs...")

    avg_match = np.mean(results)
    std_match = np.std(results)

    # Plot the distribution of match percentages
    plt.figure(figsize=(10, 6))
    sns.histplot(results, kde=True, bins=30, color='blue')
    plt.axvline(avg_match, color='red', linestyle='--', linewidth=2, label=f"Mean: {avg_match:.2f}%")
    plt.axvline(avg_match + std_match, color='green', linestyle='--', linewidth=2, label=f"Mean + 1 STD: {avg_match + std_match:.2f}%")
    plt.axvline(avg_match - std_match, color='green', linestyle='--', linewidth=2, label=f"Mean - 1 STD: {avg_match - std_match:.2f}%")

    plt.title("Distribution of Match Percentages")
    plt.xlabel("Match Percentage")
    plt.ylabel("Frequency")
    plt.legend()
    # Save the figure
    figure_file = "match_percentage_distribution_final.png"
    plt.savefig(figure_file, bbox_inches="tight")
    print(f"Figure saved as {figure_file}")

    plt.show()

    print(f"Average Match Percentage: {avg_match:.2f}")
    print(f"Standard Deviation: {std_match:.2f}")

if __name__ == "__main__":
    main()

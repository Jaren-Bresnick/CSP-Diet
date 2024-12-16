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

# existing_meal_names = set(meal_df["Meal Name"].dropna().unique())
# limited_meal_names = list(existing_meal_names)[-150:]

def gen_ai(prompt):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)

    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    return(response.text)

# meal_names_str = ", ".join(limited_meal_names)
breakfast_meals = [
    "Avocado Toast with Poached Egg", "Spinach and Feta Omelette", "Blueberry Oatmeal Pancakes",
    "Greek Yogurt with Honey and Berries", "Banana Peanut Butter Smoothie Bowl",
    "Chia Seed Pudding with Mango", "Overnight Oats with Almond Butter",
    "Cottage Cheese and Pineapple Bowl", "Scrambled Eggs with Smoked Salmon",
    "Sweet Potato Hash with Fried Egg", "Quinoa Breakfast Bowl with Fruit",
    "Apple Cinnamon Overnight Oats", "French Toast with Maple Syrup",
    "Breakfast Burrito with Eggs and Veggies", "Bagel with Cream Cheese and Lox",
    "Spinach and Mushroom Frittata", "Almond Butter Toast with Banana Slices",
    "Protein Smoothie with Berries", "Tofu Scramble with Veggies",
    "Coconut Yogurt with Granola and Berries", "Egg and Cheese Breakfast Sandwich",
    "Breakfast Quesadilla with Spinach", "Pancakes with Nutella and Strawberries",
    "Egg Muffins with Bell Peppers", "Savory Oatmeal with Soft-Boiled Egg",
    "English Muffin Breakfast Pizza", "Peanut Butter Banana Waffles",
    "Oatmeal with Cinnamon and Raisins", "Sausage and Veggie Breakfast Skillet",
    "Breakfast Tacos with Scrambled Eggs", "Smoothie Bowl with Granola",
    "Baked Avocado Eggs", "Ham and Cheese Croissant", "Muesli with Almond Milk",
    "Strawberry and Cream Cheese Crepes", "Cranberry Almond Overnight Oats",
    "Veggie-Stuffed Omelette", "Breakfast Casserole with Sausage",
    "Ricotta and Honey Toast", "Pumpkin Spice Oatmeal", "Breakfast Wrap with Turkey and Spinach",
    "Apple and Almond Butter Rice Cakes", "Eggs Benedict with Hollandaise Sauce",
    "Fruit and Nut Granola Parfait", "Savory Waffles with Cheese",
    "Shakshuka (Poached Eggs in Tomato Sauce)", "Smoked Salmon and Avocado Bagel",
    "Sweet Potato Toast with Toppings", "Breakfast Couscous with Almonds",
    "Cinnamon Raisin Bagel with Butter", "Bacon, Egg, and Cheese Bagel",
    "Pineapple Coconut Chia Bowl", "Peach and Yogurt Smoothie Bowl",
    "Oatmeal Banana Pancakes", "Almond and Date Energy Bites",
    "Cranberry Walnut Breakfast Muffins", "Sausage, Egg, and Spinach Skillet",
    "Caramelized Banana French Toast", "Breakfast Fried Rice with Eggs",
    "Mini Frittatas with Spinach", "Greek Yogurt with Almonds and Honey",
    "Raspberry and Chocolate Chip Waffles", "Tropical Smoothie with Pineapple",
    "Egg-in-a-Hole Toast", "Breakfast Burrito with Chorizo",
    "Buckwheat Pancakes with Maple Syrup", "Savory Crepes with Spinach and Cheese",
    "Black Bean and Egg Tacos", "Quiche Lorraine with Spinach",
    "Strawberry Chia Smoothie Bowl", "Bagel Sandwich with Turkey and Eggs",
    "Homemade Granola Bars", "Poached Eggs on Sourdough Toast",
    "Banana Walnut Muffins", "Spiced Apple Waffles", "Breakfast Nachos with Eggs",
    "Egg and Sausage Breakfast Casserole", "Chocolate Peanut Butter Smoothie Bowl",
    "Tomato Basil Omelette", "Baked Oatmeal with Blueberries",
    "Yogurt Parfait with Mixed Berries", "Croissant Breakfast Sandwich",
    "Spinach and Sausage Breakfast Bowl", "Pear and Almond Oatmeal",
    "Cheddar and Broccoli Frittata", "Coconut Almond Chia Pudding",
    "Zucchini and Feta Omelette", "Honey and Walnut Greek Yogurt Bowl",
    "Pancakes with Cinnamon Apples", "Bacon and Spinach Egg Cups",
    "Breakfast Sliders with Ham and Cheese", "Protein Pancakes with Almond Butter",
    "Tomato and Avocado Egg Toast", "Savory Oatmeal with Bacon",
    "Pineapple and Coconut Smoothie", "Breakfast Polenta with Mushrooms",
    "Lemon Blueberry Scones", "Chorizo and Egg Breakfast Tacos",
    "Pesto and Mozzarella Omelette", "Cinnamon Swirl Breakfast Bread"
]

lunch_dinner_meals = [
    "Grilled Chicken Caesar Salad", "Beef Stroganoff with Egg Noodles", "Teriyaki Salmon with Steamed Rice",
    "Vegetarian Lentil Curry", "Spaghetti Carbonara", "Chicken Alfredo Pasta", "Sweet and Sour Pork",
    "Thai Green Curry with Jasmine Rice", "Mushroom Risotto", "Shrimp Scampi with Garlic Butter",
    "Vegan Buddha Bowl", "BBQ Pulled Pork Sandwiches", "Turkey and Swiss Panini", "Chicken Tikka Masala",
    "Baked Ziti with Italian Sausage", "Stuffed Bell Peppers", "Beef and Broccoli Stir-Fry",
    "Seared Tuna with Mango Salsa", "Greek Gyro Wraps with Tzatziki", "Falafel with Hummus and Pita",
    "Spinach and Ricotta Ravioli", "Veggie Stir-Fry with Tofu", "Classic Meatloaf with Mashed Potatoes",
    "Chicken Enchiladas", "Roasted Duck with Orange Glaze", "Lobster Mac and Cheese",
    "Pork Chops with Apple Sauce", "Miso-Glazed Cod", "Ratatouille with Fresh Basil",
    "Korean Bibimbap", "Chicken and Waffles", "Vegetarian Chili with Cornbread",
    "Grilled Ribeye Steak with Asparagus", "Shrimp Tacos with Lime Crema", "Chicken Parmigiana",
    "Vietnamese Pho with Beef Brisket", "Spinach and Artichoke Flatbread", "Bangers and Mash",
    "Moroccan Lamb Tagine", "Sushi Rolls (California Roll, Spicy Tuna)", "Pad Thai with Shrimp",
    "Eggplant Parmesan", "Cajun Jambalaya with Sausage", "Chicken Pot Pie", "Tuna Salad Wraps",
    "Shepherd’s Pie with Lamb", "Fish and Chips with Tartar Sauce", "Lasagna Bolognese",
    "Thai Basil Chicken", "Vegan Chickpea Stew", "Roasted Vegetable Quiche",
    "Crab Cakes with Remoulade Sauce", "Classic Cobb Salad", "Grilled Salmon with Dill Sauce",
    "Hawaiian Pizza with Ham and Pineapple", "Chicken Fried Rice", "Steak Fajitas with Guacamole",
    "French Onion Soup with Cheese Toast", "Baked Cod with Lemon Butter", "Veggie Quesadillas",
    "Pulled Beef Tacos", "Mushroom and Spinach Stroganoff", "Chicken Shawarma Plate",
    "Ramen Noodles with Soft-Boiled Egg", "Sweet Potato and Black Bean Tacos",
    "Roasted Turkey Breast with Cranberry Sauce", "Crab-Stuffed Mushrooms", "Sausage and Peppers Pasta",
    "Tofu Pad See Ew", "Pesto Pasta with Cherry Tomatoes", "Indian Butter Chicken",
    "Pork Schnitzel with Potato Salad", "Veggie Burgers with Sweet Potato Fries",
    "Lemon Garlic Shrimp over Linguine", "BBQ Chicken Pizza", "Beef Tacos with Salsa Verde",
    "Moussaka with Eggplant and Ground Beef", "Sesame Ginger Chicken Stir-Fry", "Teriyaki Tofu Bowls",
    "Chicken Tortilla Soup", "Lobster Bisque with Crusty Bread", "Chili Lime Grilled Chicken",
    "Pork Belly Bao Buns", "Vegetarian Poke Bowl", "Garlic Butter Scallops with Rice Pilaf",
    "Classic Tuna Casserole", "Beef Chili with Jalapeno Cornbread", "Vegan Mushroom Stroganoff",
    "Korean Fried Chicken", "Shrimp Etouffee", "BBQ Ribs with Coleslaw", "Lemon Herb Roasted Chicken",
    "Egg Salad Sandwiches", "Spinach and Feta Stuffed Chicken", "Vegetarian Paella with Artichokes",
    "Blackened Catfish with Cajun Rice", "Beef Wellington with Red Wine Sauce",
    "Teriyaki Glazed Meatballs", "Caprese Salad with Balsamic Glaze", "Salmon Burgers with Dill Sauce",
    "Penne Arrabbiata", "Thai Massaman Curry", "Chicken and Sausage Gumbo",
    "Grilled Swordfish with Pineapple Salsa", "Philly Cheesesteak Sandwiches", "Vegan Shepherd’s Pie",
    "Roasted Cauliflower Steaks", "Spanish Chorizo Paella", "Spaghetti Marinara with Meatballs",
    "Seared Duck Breast with Cherry Sauce", "Roasted Brussel Sprouts and Bacon Salad",
    "Ahi Tuna Poke Bowls", "Sweet Corn Tamales", "Buffalo Chicken Wraps", "Shrimp Creole with Rice",
    "Pork Ramen Noodle Bowl", "Lemon Zest Risotto with Asparagus", "Grilled Veggie and Hummus Wraps",
    "Thai Drunken Noodles with Chicken", "Lentil Soup with Crusty Bread", "Smoked Salmon Pasta",
    "Chicken Alfredo Lasagna", "Mediterranean Grain Bowl", "Beef Kebab with Garlic Sauce",
    "Peking Duck with Hoisin Sauce", "Zucchini Noodles with Pesto", "Roasted Lamb with Mint Sauce",
    "BBQ Jackfruit Sandwiches", "Chicken Satay Skewers", "Cheesy Baked Potatoes",
    "Butternut Squash Ravioli", "Spinach and Goat Cheese Pizza", "Stuffed Cabbage Rolls",
    "Thai Panang Curry", "Garlic Shrimp Alfredo", "Beef and Potato Stew",
    "Veggie Samosas with Tamarind Chutney", "Roast Beef Sandwiches with Horseradish",
    "Sesame Crusted Salmon", "Creamy Tomato Basil Soup", "Lobster Roll Sandwiches",
    "Indian Aloo Gobi Curry", "Chicken Marsala with Mushrooms", "Spaghetti Squash with Meat Sauce",
    "Grilled Mahi Mahi with Lime Butter", "Clam Chowder in a Bread Bowl", "Tofu Katsu Curry",
    "Fettuccine Alfredo with Spinach", "Hawaiian Loco Moco", "Pork Carnitas Tacos",
    "Veggie Pizza with Arugula", "Baked Salmon with Mustard Glaze", "Kimchi Fried Rice",
    "Grilled Portobello Mushroom Burger", "Baked Chicken Tenders with Honey Mustard",
    "Coconut Curry Shrimp", "Stuffed Acorn Squash", "Chicken and Dumplings",
    "Spicy Thai Shrimp Soup", "Sloppy Joes with Pickles", "Tuna Nicoise Salad",
    "Grilled Halloumi Salad", "Pumpkin Risotto with Sage", "Teriyaki Beef Skewers",
    "Stuffed Zucchini Boats", "Roasted Duck Breast with Blackberry Sauce",
    "Shredded Chicken Tostadas", "BBQ Pulled Jackfruit Sliders", "Eggplant Rollatini",
    "Lemon Chicken Piccata", "Italian Sausage and Spinach Soup", "Vegan Burrito Bowls",
    "Grilled Chicken and Mango Salsa", "Lentil and Sweet Potato Stew", "BBQ Shrimp with Cornbread",
    "Beef Pho with Fresh Herbs", "Mushroom Alfredo Pasta", "Crispy Fish Tacos",
    "Buttered Lobster Tail", "Pulled Pork Nachos", "Chicken Schnitzel with Lemon Butter",
    "Cauliflower Buffalo Wings", "Cuban Sandwich with Pork", "Indian Saag Paneer",
    "Thai Curry Noodle Soup", "Grilled Shrimp Caesar Salad", "Roasted Pork Tenderloin",
    "Vegan Pad Thai", "Chicken and Broccoli Stir-Fry", "Slow-Cooked Beef Ragu",
    "Roasted Red Pepper Hummus Wrap", "Shrimp and Grits", "Italian Wedding Soup",
    "Korean Bulgogi with Rice", "Baked Eggplant Parmesan", "Roast Chicken with Root Vegetables",
    "Seared Scallops with Lemon Butter", "Moroccan Couscous with Vegetables",
    "Beef Tostadas with Guacamole", "Classic Chicken Piccata"
]

soups_and_stews_meals = [
    "Classic Chicken Noodle Soup",
    "Beef and Barley Stew",
    "Creamy Tomato Basil Soup",
    "Lentil and Spinach Soup",
    "French Onion Soup with Cheese Croutons",
    "Hearty Vegetable Stew",
    "Thai Coconut Chicken Soup (Tom Kha Gai)",
    "Beef Chili with Kidney Beans",
    "Potato Leek Soup",
    "Moroccan Chickpea Stew",
    "Clam Chowder in a Bread Bowl",
    "Sweet Potato and Black Bean Chili",
    "Split Pea Soup with Ham",
    "Tuscan White Bean Soup with Kale",
    "Korean Kimchi Jjigae (Kimchi Stew)",
    "Shrimp and Corn Chowder",
    "Vegetarian Minestrone Soup",
    "Cream of Mushroom Soup",
    "Italian Wedding Soup",
    "Japanese Miso Soup with Tofu",
    "Butternut Squash Soup with Ginger",
    "Spicy Thai Red Curry Soup",
    "Slow-Cooked Beef Stew with Red Wine",
    "Mexican Tortilla Soup",
    "Turkey and Wild Rice Soup",
    "Pho with Beef Brisket and Herbs",
    "Hungarian Goulash Stew",
    "Cabbage and Sausage Soup",
    "Pumpkin and Carrot Soup with Nutmeg",
    "Vegan Lentil and Sweet Potato Stew",
    "Seafood Gumbo with Okra",
    "Borscht (Beet Soup)",
    "Chicken and Dumplings",
    "Chorizo and White Bean Stew",
    "Coconut Curry Butternut Squash Soup",
    "New England Lobster Bisque",
    "Creamy Cauliflower Soup with Parmesan",
    "Indian Dal Tadka (Lentil Stew)",
    "Italian Ribollita (Bread Soup)",
    "Spicy Black Bean Soup",
    "Creamy Broccoli Cheddar Soup",
    "Vegetable Mulligatawny Soup",
    "Irish Lamb Stew with Potatoes",
    "Chicken Pozole Verde",
    "African Peanut Stew with Sweet Potatoes",
    "Corn and Zucchini Chowder",
    "Japanese Ramen with Soft-Boiled Egg",
    "Curry Pumpkin Soup with Coconut Milk",
    "Pork and Cabbage Stew",
    "Ham and Bean Soup"
]

salad_meals = [
    "Classic Caesar Salad",
    "Greek Salad with Feta and Olives",
    "Caprese Salad with Balsamic Glaze",
    "Spinach and Strawberry Salad",
    "Kale and Quinoa Salad",
    "Cobb Salad with Chicken and Bacon",
    "Asian Sesame Chicken Salad",
    "Mexican Street Corn Salad (Elote Salad)",
    "Mediterranean Chickpea Salad",
    "Beet and Goat Cheese Salad",
    "Waldorf Salad with Apples and Walnuts",
    "Arugula Salad with Lemon Vinaigrette",
    "Roasted Sweet Potato and Black Bean Salad",
    "Thai Green Papaya Salad",
    "Crunchy Broccoli Salad with Raisins",
    "Watermelon and Feta Salad",
    "Avocado and Tomato Salad with Cilantro Lime Dressing",
    "Grilled Peach and Burrata Salad",
    "Shrimp Louie Salad",
    "Orzo Pasta Salad with Sun-Dried Tomatoes",
    "Buffalo Chicken Salad with Blue Cheese",
    "Farro Salad with Roasted Vegetables",
    "Grilled Chicken and Avocado Salad",
    "Antipasto Salad with Salami and Mozzarella",
    "Sesame Ginger Noodle Salad",
    "Roasted Beet and Arugula Salad",
    "Zucchini Ribbon Salad with Lemon Dressing",
    "Fruit Salad with Honey Lime Glaze",
    "Niçoise Salad with Tuna and Potatoes",
    "Warm Lentil Salad with Spinach",
    "Tabbouleh Salad with Fresh Parsley",
    "Grilled Steak Salad with Chimichurri",
    "Southwest Salad with Avocado Ranch Dressing",
    "Shaved Brussels Sprouts Salad with Pecans",
    "Greek Orzo Salad with Lemon Dressing",
    "Cucumber and Dill Salad",
    "Asian Slaw with Peanut Dressing",
    "Pomegranate and Kale Salad with Walnuts",
    "Spinach and Mushroom Salad with Warm Bacon Dressing",
    "Carrot and Raisin Salad with Pineapple",
    "BLT Salad with Buttermilk Dressing",
    "Tropical Mango and Avocado Salad",
    "Quinoa and Edamame Salad",
    "Grilled Salmon Salad with Dill Dressing",
    "Roasted Cauliflower and Chickpea Salad",
    "Green Goddess Salad with",
    "Shrimp and Avocado Salad with Lime",
    "Pasta Salad with Italian Dressing",
    "Tex-Mex Taco Salad with Ground Beef",
    "Mixed Berry Salad with Honey Yogurt Dressing"
]


limited_breakfast_meals = list(breakfast_meals)[90:100]
limited_lunch_meals = list(lunch_dinner_meals)[184:200]
limited_soups_meals = list(soups_and_stews_meals)[40:50]
limited_salad_meals = list(salad_meals)[46:50]

prompt = f"""
    For every meal in {limited_salad_meals} generate a list in the following format:
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


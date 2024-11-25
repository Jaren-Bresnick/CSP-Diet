import pandas as pd

# Sample meal database
data = pd.read_csv('mealDB.csv')

# Convert data to a DataFrame
df = pd.DataFrame(data)

# User constraints and preferences
user_constraints = {
    "max_calories_per_meal": 600,
    "preferred_cuisines": ["Italian", "Japanese"],
    "meal_types": ["breakfast", "lunch", "dinner", "snack"],
    "temperature_preference": "hot",
    "vegetarian_only": True
}

# Optimization weights
weights = {
    "cuisine_weight": 3,
    "temperature_weight": 2
}

# Filter the database to form a reduced domain based on hard constraints
def filter_meals(df, constraints):
    filtered_df = df[
        (df['calories'] <= constraints["max_calories_per_meal"]) &
        (df['type'].isin(constraints["meal_types"])) &
        (df['vegetarian'] == constraints["vegetarian_only"])
    ]
    return filtered_df

filtered_meals = filter_meals(df, user_constraints)

# Scoring function for preferences
def calculate_score(meal, constraints, weights):
    score = 0
    if meal['cuisine'] in constraints["preferred_cuisines"]:
        score += weights["cuisine_weight"]
    if meal['temperature'] == constraints["temperature_preference"]:
        score += weights["temperature_weight"]
    return score

# DFS function to explore meal combinations
def dfs(meals, current_plan, used_types, best_plan, best_score, constraints, weights):
    # If we have a meal for every type, evaluate the plan
    if len(used_types) == len(constraints["meal_types"]):
        current_score = sum([meal['score'] for meal in current_plan])
        if current_score > best_score[0]:
            best_score[0] = current_score
            best_plan.clear()
            best_plan.extend(current_plan)
        return

    for _, meal in meals.iterrows():
        if meal['type'] not in used_types:
            # Add meal to the current plan
            meal_with_score = meal.copy()
            meal_with_score['score'] = calculate_score(meal, constraints, weights)
            current_plan.append(meal_with_score)
            used_types.add(meal['type'])

            # Recurse
            dfs(meals, current_plan, used_types, best_plan, best_score, constraints, weights)

            # Backtrack
            current_plan.pop()
            used_types.remove(meal['type'])

# Run DFS to find the best meal plan
best_plan = []
best_score = [0]  # Use a mutable object to track the best score
dfs(filtered_meals, [], set(), best_plan, best_score, user_constraints, weights)

# Output the best plan
best_plan_df = pd.DataFrame(best_plan)
print("Best meal plan:")
print(best_plan_df)

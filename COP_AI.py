import pandas as pd

# Sample meal database
data = {
    'meal_id': [1, 2, 3, 4, 5, 6],
    'meal_name': ['Pasta', 'Salad', 'Sushi', 'Pizza', 'Soup', 'Sandwich'],
    'calories': [500, 300, 400, 800, 200, 600],
    'cuisine': ['Italian', 'Mediterranean', 'Japanese', 'Italian', 'Asian', 'American'],
    'type': ['lunch', 'lunch', 'dinner', 'dinner', 'lunch', 'breakfast'],
    'vegetarian': [True, True, True, True, True, True]
}

# Convert data to a DataFrame
df = pd.DataFrame(data)
print(df)

# User constraints and preferences
user_constraints = {
    "target_calories": 1500,
    "preferred_cuisines": ["Italian", "Japanese", "American"],
    "meal_types": ["breakfast", "lunch", "dinner"],  
    "vegetarian_only": True
}

# Optimization weights
weights = {
    "cuisine_weight": 3
}

# Filter meals based on hard constraints
def filter_meals(df, constraints):
    filtered_df = df[
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
    return score

# Constraint optimization function
def constraint_optimization(meals, meal_types, constraints, weights):
    best_plan = []
    best_score = float('inf')  # We minimize the absolute calorie difference

    # Recursive function to explore all valid combinations
    def explore(current_plan, remaining_meals, used_types, current_calories, current_pref_score):
        nonlocal best_plan, best_score

        # If all meal types are used, check if this plan is optimal
        if len(used_types) == len(meal_types):
            calorie_diff = abs(current_calories - constraints["target_calories"])
            if calorie_diff < best_score:  # Minimize calorie difference
                best_score = calorie_diff
                best_plan = current_plan[:]
            return

        # Explore remaining meals
        for i, meal in enumerate(remaining_meals):
            if meal['type'] not in used_types:
                # Calculate the preference score for the current meal
                meal_with_score = meal.copy()
                meal_with_score['score'] = calculate_score(meal, constraints, weights)

                # Add meal to the current plan
                current_plan.append(meal_with_score)
                used_types.add(meal['type'])

                # Recurse with updated plan and remaining meals
                explore(
                    current_plan,
                    remaining_meals[i + 1:],
                    used_types,
                    current_calories + meal['calories'],
                    current_pref_score + meal_with_score['score']
                )

                # Backtrack
                current_plan.pop()
                used_types.remove(meal['type'])

    # Start exploration with an empty plan
    explore([], filtered_meals.to_dict('records'), set(), 0, 0)

    return best_plan, best_score

# Solve the problem
best_plan, best_score = constraint_optimization(filtered_meals, user_constraints["meal_types"], user_constraints, weights)

# Convert best_plan to DataFrame if it is not empty
if best_plan:
    best_plan_df = pd.DataFrame(best_plan)
    print("Best meal plan:")
    print(best_plan_df)
    print(f"Total Calories: {best_plan_df['calories'].sum()} (Target: {user_constraints['target_calories']})")
    print(f"Calorie Difference: {best_score}")
else:
    print("No feasible solution found.")
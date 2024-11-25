from ortools.sat.python import cp_model
import pandas as pd

# Sample meal database
data = {
    'meal_id': [1, 2, 3, 4, 5, 6],
    'meal_name': ['Pasta', 'Salad', 'Sushi', 'Pizza', 'Soup', 'Sandwich'],
    'calories': [500, 300, 400, 800, 200, 600],
    'cuisine': ['Italian', 'Mediterranean', 'Japanese', 'Italian', 'Asian', 'American'],
    'type': ['lunch', 'lunch', 'dinner', 'dinner', 'snack', 'breakfast'],
    'vegetarian': [True, True, False, False, True, True]
}

# Convert data to a DataFrame
df = pd.DataFrame(data)

# User constraints and preferences
user_constraints = {
    "target_calories": 1500,
    "preferred_cuisines": ["Italian", "Japanese"],
    "meal_types": ["breakfast", "lunch", "dinner", "snack"],
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

# Initialize the model
model = cp_model.CpModel()

# Variables
meal_vars = {}
for index, row in filtered_meals.iterrows():
    meal_vars[row['meal_id']] = model.NewBoolVar(f"meal_{row['meal_id']}")

# Constraints
# 1. Select exactly one meal for each meal type
for meal_type in user_constraints["meal_types"]:
    type_meals = filtered_meals[filtered_meals['type'] == meal_type]
    model.Add(sum(meal_vars[meal['meal_id']] for _, meal in type_meals.iterrows()) == 1)

# Objective: Minimize the absolute difference between total calories and target
total_calories = sum(meal_vars[row['meal_id']] * row['calories'] for _, row in filtered_meals.iterrows())
target_calories = user_constraints["target_calories"]

# Add auxiliary variable for the absolute difference
diff = model.NewIntVar(0, sum(filtered_meals['calories']), 'calorie_diff')
model.Add(diff == abs(total_calories - target_calories))

# Add preference scoring for cuisines
cuisine_scores = {
    meal['meal_id']: weights["cuisine_weight"] if meal['cuisine'] in user_constraints["preferred_cuisines"] else 0
    for _, meal in filtered_meals.iterrows()
}
preference_score = sum(meal_vars[meal_id] * score for meal_id, score in cuisine_scores.items())

# Objective: Minimize calorie difference, maximize preference score
model.Minimize(diff - preference_score)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Output the results
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("Optimal meal plan:")
    selected_meals = []
    for meal_id, var in meal_vars.items():
        if solver.Value(var):
            selected_meals.append(filtered_meals[filtered_meals['meal_id'] == meal_id].iloc[0])
    selected_meals_df = pd.DataFrame(selected_meals)
    print(selected_meals_df)
    print(f"Total Calories: {solver.Value(total_calories)} (Target: {target_calories})")
    print(f"Calorie Difference: {solver.Value(diff)}")
else:
    print("No feasible solution found.")

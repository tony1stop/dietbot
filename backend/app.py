from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Your OAuth 2.0 credentials
CLIENT_ID = 'db0b9aee846d461f913e63cf3083f12e'
CLIENT_SECRET = '2a44e2646220498cb8e8ba88087481c1'

# Token endpoint
TOKEN_URL = 'https://oauth.fatsecret.com/connect/token'

# Base URL for FatSecret API
BASE_URL = 'https://platform.fatsecret.com/rest/server.api'

# Function to get an access token
def get_access_token():
    data = {
        'grant_type': 'client_credentials',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'basic'  # Adjust the scope as needed
    }
    response = requests.post(TOKEN_URL, data=data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")

# Function to search for foods
def search_foods(query, max_results=5):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'method': 'foods.search',
        'format': 'json',
        'search_expression': query,
        'max_results': max_results
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['foods']['food']
    else:
        return []

# Function to get nutritional information for a specific food
def get_food_nutrition(food_id):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'method': 'food.get',
        'format': 'json',
        'food_id': food_id
    }
    response = requests.get(BASE_URL, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()['food']
    else:
        return None

# Function to fetch a meal based on dietary preferences
def fetch_meal(diet, max_calories):
    # Search for foods based on dietary preferences
    foods = search_foods(diet, max_results=1)
    if foods:
        food_id = foods[0]['food_id']
        food_details = get_food_nutrition(food_id)
        if food_details:
            return {
                "name": food_details['food_name'],
                "calories": food_details['calories'],
                "protein": food_details['protein'],
                "carbs": food_details['carbohydrate'],
                "fat": food_details['fat'],
                "ingredients": [food_details['food_name']]  # Placeholder for ingredients
            }
    return None

# Function to calculate daily caloric needs
def calculate_calories(age, gender, weight_kg, height_cm, activity, goal):
    if gender == "male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725
    }
    maintenance = bmr * activity_multipliers[activity]

    if goal == "loss":
        return maintenance - 500  # Subtract 500 calories for weight loss
    elif goal == "gain":
        return maintenance + 500  # Add 500 calories for weight gain
    else:
        return maintenance

# Function to calculate macros
def calculate_macros(calories, goal, workout_preference):
    protein = calories * 0.30 / 4  # 30% of calories from protein
    fat = calories * 0.25 / 9      # 25% of calories from fat
    carbs = calories * 0.45 / 4    # 45% of calories from carbs

    # Adjust carbs based on workout preference
    if workout_preference == "fuelWorkout":
        carbs += 50  # Add extra carbs for energy and recovery
    elif workout_preference == "recoverStrong":
        carbs += 30  # Add extra carbs for recovery
    elif workout_preference == "burnFat":
        carbs -= 20  # Reduce carbs for fasted workouts

    return {
        "protein": round(protein, 1),
        "fat": round(fat, 1),
        "carbs": round(carbs, 1)
    }

# Function to generate a meal plan
def generate_meal_plan(days, meals_per_day, calories, macros, diet, workout_time, workout_preference):
    meal_plan = []
    grocery_list = set()

    for day in range(1, days + 1):
        daily_meals = []
        for meal_num in range(1, meals_per_day + 1):
            # Fetch a meal based on dietary preferences and macros
            meal = fetch_meal(diet, calories // meals_per_day)
            if meal:
                daily_meals.append(meal)
                grocery_list.update(meal['ingredients'])  # Add ingredients to grocery list

        meal_plan.append({
            "day": day,
            "meals": daily_meals,
            "macros": macros
        })

    return {
        "meal_plan": meal_plan,
        "grocery_list": list(grocery_list)
    }

# Route to handle form submission
@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.json
    unit_system = data['unitSystem']

    # Convert weight and height to metric if necessary
    if unit_system == 'imperial':
        weight_kg = float(data['weight']) * 0.453592  # Convert pounds to kilograms
        height_cm = (float(data['heightFeet']) * 30.48) + (float(data['heightInches']) * 2.54)  # Convert feet/inches to centimeters
    else:
        weight_kg = float(data['weight'])
        height_cm = float(data['heightCm'])

    # Calculate calories and macros
    calories = calculate_calories(int(data['age']), data['gender'], weight_kg, height_cm, data['activity'], data['goal'])
    macros = calculate_macros(calories, data['goal'], data['workoutPreference'])

    # Generate meal plan
    meal_plan = generate_meal_plan(
        days=int(data['days']),
        meals_per_day=int(data['mealsPerDay']),
        calories=calories,
        macros=macros,
        diet=data['diet'],
        workout_time=data['workoutTime'],
        workout_preference=data['workoutPreference']
    )

    return jsonify(meal_plan)

if __name__ == '__main__':
    app.run(debug=True)
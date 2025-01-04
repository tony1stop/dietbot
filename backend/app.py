from flask import Flask, request, jsonify
from flask_cors import CORS  # To handle CORS issues

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Function to calculate daily caloric needs
def calculate_calories(age, gender, weight, height, activity, goal):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

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

# Route to handle form submission
@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.json
    age = int(data['age'])
    gender = data['gender']
    weight = float(data['weight'])
    height = float(data['height'])
    activity = data['activity']
    goal = data['goal']

    calories = calculate_calories(age, gender, weight, height, activity, goal)

    # For now, return a simple response
    meal_plan = {
        "calories": calories,
        "meals": [
            "Breakfast: Greek yogurt with berries",
            "Lunch: Quinoa salad",
            "Snack: Apple with almond butter",
            "Dinner: Grilled chicken with veggies"
        ]
    }
    return jsonify(meal_plan)

if __name__ == '__main__':
    app.run(debug=True)
// Function to toggle between metric and imperial height inputs
document.getElementById('unitSystem').addEventListener('change', function () {
    const unitSystem = this.value; // Get the selected unit system
    const heightMetric = document.getElementById('heightMetric'); // Metric height input
    const heightImperial = document.getElementById('heightImperial'); // Imperial height input

    if (unitSystem === 'metric') {
        // Show metric input and hide imperial input
        heightMetric.style.display = 'block';
        heightImperial.style.display = 'none';
    } else {
        // Show imperial input and hide metric input
        heightMetric.style.display = 'none';
        heightImperial.style.display = 'block';
    }
});

// Form submission logic
document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get the selected unit system
    const unitSystem = document.getElementById('unitSystem').value;

    // Prepare data object
    const data = {
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        weight: document.getElementById('weight').value,
        activity: document.getElementById('activity').value,
        goal: document.getElementById('goal').value,
        diet: document.getElementById('diet').value,
        days: document.getElementById('days').value,
        mealsPerDay: document.getElementById('mealsPerDay').value,
        workoutTime: document.getElementById('workoutTime').value,
        workoutPreference: document.getElementById('workoutPreference').value,
        unitSystem: unitSystem, // Add unit system to the data
    };

    // Add height based on the selected unit system
    if (unitSystem === 'metric') {
        data.heightCm = document.getElementById('heightCm').value;
    } else {
        data.heightFeet = document.getElementById('heightFeet').value;
        data.heightInches = document.getElementById('heightInches').value;
    }

    try {
        const response = await fetch('http://127.0.0.1:5000/generate-plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();

        // Display the meal plan
        const mealPlanDiv = document.getElementById('mealPlan');
        mealPlanDiv.innerHTML = `
            <h3>Your ${result.days}-Day Meal Plan (${result.calories} calories/day):</h3>
            ${result.meal_plan.map(day => `
                <div>
                    <h4>Day ${day.day}</h4>
                    <ul>
                        ${day.meals.map(meal => `
                            <li>
                                <strong>${meal.name}</strong> (${meal.calories} calories)
                                <br>Protein: ${meal.protein}g, Carbs: ${meal.carbs}g, Fat: ${meal.fat}g
                            </li>
                        `).join('')}
                    </ul>
                </div>
            `).join('')}
            <h3>Grocery List:</h3>
            <ul>
                ${result.grocery_list.map(item => `<li>${item}</li>`).join('')}
            </ul>
        `;
    } catch (error) {
        console.error('Error:', error);
    }
});
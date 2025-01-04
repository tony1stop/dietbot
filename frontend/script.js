document.getElementById('userForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const data = {
        age: document.getElementById('age').value,
        gender: document.getElementById('gender').value,
        weight: document.getElementById('weight').value,
        height: document.getElementById('height').value,
        activity: document.getElementById('activity').value,
        goal: document.getElementById('goal').value
    };

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
            <h3>Your Meal Plan (${result.calories} calories/day):</h3>
            <ul>
                ${result.meals.map(meal => `<li>${meal}</li>`).join('')}
            </ul>
        `;
    } catch (error) {
        console.error('Error:', error);
    }
});
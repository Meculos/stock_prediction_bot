document.addEventListener('DOMContentLoaded', () => {
    const predictForm = document.getElementById('predictForm');
    const tickerInput = document.getElementById('ticker');
    const resultDiv = document.getElementById('predictionResult');

    predictForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        resultDiv.innerHTML = "";

        const ticker = tickerInput.value.trim().toUpperCase();
        if (!ticker) {
            resultDiv.innerHTML = `<p class="text-red-600">Please enter a valid ticker symbol.</p>`;
            return;
        }

        const token = localStorage.getItem('access_stock_bot');
        if (!token) {
            resultDiv.innerHTML = `<p class="text-red-600">You must be logged in to predict a stock.</p>`;
            return;
        }

        try {
            const response = await fetch('/api/v1/predict/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ ticker })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || "An error occurred.");
            }

            const { next_day_price, mse, rmse, r2, plot_urls } = data;

            resultDiv.innerHTML = `
                <div class="mb-4 p-4 bg-green-50 border border-green-300 rounded">
                    <p class="text-lg font-semibold">Predicted Price: <span class="text-green-700">₦${next_day_price}</span></p>
                    <p>MSE: ${mse}</p>
                    <p>RMSE: ${rmse}</p>
                    <p>R² Score: ${r2}</p>
                </div>
                <div class="flex flex-col md:flex-row gap-4">
                    <img src="${plot_urls[0]}" alt="Closing History Chart" class="w-full md:w-1/2 rounded shadow">
                    <img src="${plot_urls[1]}" alt="Prediction vs Actual Chart" class="w-full md:w-1/2 rounded shadow">
                </div>
            `;
        } catch (error) {
            resultDiv.innerHTML = `<p class="text-red-600">${error.message}</p>`;
        }
    });
});

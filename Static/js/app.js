document.addEventListener('DOMContentLoaded', () => {
    const predictionForm = document.getElementById('prediction-form');
    const stockTickerInput = document.getElementById('stock-ticker');
    const tickerResult = document.getElementById('ticker-result');
    const predictionPrice = document.getElementById('prediction-price');
    const currentPrice = document.getElementById('current-price'); // New element for current stock price
    const loadingSpinner = document.getElementById('loading-spinner'); // Optional: Add a loading spinner to show while fetching

    let predictionChart;  // Declare a variable to store the chart instance

    // Clear previous results
    function clearResults() {
        tickerResult.textContent = '-';
        predictionPrice.textContent = '-';
        currentPrice.textContent = 'Current Price: $-';
        document.getElementById('future-1-day').textContent = '-';
        document.getElementById('future-15-days').textContent = '-';
        document.getElementById('future-30-days').textContent = '-';
    }

    // Show the loading spinner
    function showLoading() {
        loadingSpinner.style.display = 'block'; // Display loading spinner
        document.getElementById('current-price').style.display = 'none';
        document.getElementById('prediction-price').style.display = 'none';
    }

    // Hide the loading spinner
    function hideLoading() {
        loadingSpinner.style.display = 'none'; // Hide loading spinner
        document.getElementById('current-price').style.display = 'block';
        document.getElementById('prediction-price').style.display = 'block';
    
    }

    // Function to destroy existing chart instance
    function destroyChart() {
        if (predictionChart) {
            predictionChart.destroy(); // Destroy the existing chart
        }
    }

    predictionForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const stockTicker = stockTickerInput.value.trim();
        if (!stockTicker) {
            alert('Please enter a valid stock ticker.');
            return;
        }

        // Clear previous results before fetching new data
        clearResults();
        showLoading(); // Show the loading spinner

        try {
            // Fetch prediction data from the backend
            const response = await fetch('/api/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ ticker: stockTicker })
            });

            if (!response.ok) {
                throw new Error('Failed to fetch prediction data');
            }

            const data = await response.json();

            if (data.error) {
                throw new Error(data.error); // Show error message from backend
            }

            // Update the UI with prediction results
            tickerResult.textContent = stockTicker.toUpperCase();
            predictionPrice.textContent = `$${data[1][0].toFixed(2)}`;

            // Display current stock price
            currentPrice.textContent = `Current Price: $${data.current_price}`;

            // Display future predictions in the table
            document.getElementById('future-1-day').textContent = `$${data[1][0].toFixed(2)}`;
            document.getElementById('future-15-days').textContent = data[15].map(price => `$${price.toFixed(2)}`).join(', ');
            document.getElementById('future-30-days').textContent = data[30].map(price => `$${price.toFixed(2)}`).join(', ');

            // Destroy the previous chart (if any) before creating a new one
            destroyChart();

            // Create Chart.js chart for predictions
            const ctx = document.getElementById('predictionChart').getContext('2d');
            const chartData = {
                labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
                datasets: [{
                    label: 'Predicted Stock Price',
                    data: data[30], // Use the 30-day predictions
                    borderColor: '#1F8A70',
                    backgroundColor: 'rgba(31, 138, 112, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            };

            const chartOptions = {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#333',
                        }
                    },
                    y: {
                        ticks: {
                            color: '#333',
                        }
                    }
                }
            };

            // Create the new chart instance
            predictionChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: chartOptions
            });

            // Make the future predictions section visible
            document.getElementById('prediction-results').classList.add('active');
        } catch (error) {
            console.error('Error fetching prediction:', error);
            alert('An error occurred while fetching the prediction. Please try again.');
        } finally {
            hideLoading(); // Hide the loading spinner after the request is done
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    // =======================
    // Prediction Form Script
    // =======================
    const predictionForm = document.getElementById('prediction-form');
    const stockTickerInput = document.getElementById('stock-ticker');
    const tickerResult = document.getElementById('ticker-result');
    const predictionPrice = document.getElementById('prediction-price');
    const currentPrice = document.getElementById('current-price');
    const loadingSpinner = document.getElementById('loading-spinner');
    let predictionChart;

    if (predictionForm) {
        function clearResults() {
            tickerResult.textContent = '-';
            predictionPrice.textContent = '-';
            currentPrice.textContent = 'Current Price: $-';
            document.getElementById('future-1-day').textContent = '-';
            document.getElementById('future-15-days').textContent = '-';
            document.getElementById('future-30-days').textContent = '-';
        }

        function showLoading() {
            loadingSpinner.style.display = 'block';
            document.getElementById('current-price').style.display = 'none';
            document.getElementById('prediction-price').style.display = 'none';
        }

        function hideLoading() {
            loadingSpinner.style.display = 'none';
            document.getElementById('current-price').style.display = 'block';
            document.getElementById('prediction-price').style.display = 'block';
        }

        function destroyChart() {
            if (predictionChart) {
                predictionChart.destroy();
            }
        }

        predictionForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const stockTicker = stockTickerInput.value.trim();
            if (!stockTicker) {
                alert('Please enter a valid stock ticker.');
                return;
            }

            clearResults();
            showLoading();

            try {
                const response = await fetch('/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ ticker: stockTicker })
                });

                if (!response.ok) {
                    throw new Error('Failed to fetch prediction data');
                }

                const data = await response.json();

                if (data.error) {
                    throw new Error(data.error);
                }

                tickerResult.textContent = stockTicker.toUpperCase();
                predictionPrice.textContent = `$${data[1][0].toFixed(2)}`;
                currentPrice.textContent = `Current Price: $${data.current_price}`;

                document.getElementById('future-1-day').textContent = `$${data[1][0].toFixed(2)}`;
                document.getElementById('future-15-days').textContent = data[15].map(price => `$${price.toFixed(2)}`).join(', ');
                document.getElementById('future-30-days').textContent = data[30].map(price => `$${price.toFixed(2)}`).join(', ');

                destroyChart();

                const ctx = document.getElementById('predictionChart').getContext('2d');
                const chartData = {
                    labels: Array.from({ length: 30 }, (_, i) => `Day ${i + 1}`),
                    datasets: [{
                        label: 'Predicted Stock Price',
                        data: data[30],
                        borderColor: '#1F8A70',
                        backgroundColor: 'rgba(31, 138, 112, 0.2)',
                        fill: true,
                        tension: 0.4
                    }]
                };

                const chartOptions = {
                    responsive: true,
                    plugins: {
                        legend: { position: 'top' },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        x: { ticks: { color: '#333' } },
                        y: { ticks: { color: '#333' } }
                    }
                };

                predictionChart = new Chart(ctx, {
                    type: 'line',
                    data: chartData,
                    options: chartOptions
                });

                document.getElementById('prediction-results').classList.add('active');
            } catch (error) {
                console.error('Error fetching prediction:', error);
                alert('An error occurred while fetching the prediction. Please try again.');
            } finally {
                hideLoading();
            }
        });
    }

// ========================
// News Carousel Script
// ========================
const slides = document.querySelectorAll('.news-slide');
let currentIndex = 0;
const slideCounter = document.getElementById('slideCounter');

function updateCounter() {
    if (slideCounter) {
        slideCounter.textContent = `${currentIndex + 1} / ${slides.length}`;
    }
}

function showSlide(index) {
    slides.forEach((slide, i) => {
        if (i === index) {
            slide.classList.add('active');
        } else {
            slide.classList.remove('active');
        }
    });
}


function nextSlide() {
    currentIndex = (currentIndex + 1) % slides.length;
    showSlide(currentIndex);
    updateCounter();
}

function prevSlide() {
    currentIndex = (currentIndex - 1 + slides.length) % slides.length;
    showSlide(currentIndex);
    updateCounter();
}

if (slides.length > 0) {
    showSlide(currentIndex);
    updateCounter();

    setInterval(nextSlide, 4000); // ✅ Start interval only once, not inside showSlide()

    const nextButton = document.getElementById('nextSlide');
    const prevButton = document.getElementById('prevSlide');

    if (nextButton && prevButton) {
        nextButton.addEventListener('click', nextSlide);
        prevButton.addEventListener('click', prevSlide);
    }
}
});

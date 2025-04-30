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
            
            // Also hide current and prediction prices
            currentPrice.style.display = 'none';
            predictionPrice.style.display = 'none';
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
                currentPrice.innerHTML = `<strong>Current Price:</strong> $${data.current_price}`;
                predictionPrice.innerHTML = `<strong>Predicted Price:</strong> $${data[1][0].toFixed(2)}`;
                

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

    // ========================
    // Notification and Mode Toggle
    // ========================
    const notificationIcon = document.getElementById('notification-icon');
    const notificationsTab = document.getElementById('notifications-tab');
    const modeIcon = document.getElementById('mode-icon');
    const body = document.getElementById('body');

    // Apply dark mode based on stored preference
    if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');  // Apply dark mode if saved
        // modeIcon.querySelector('i').classList.remove('fa-moon');
        // modeIcon.querySelector('i').classList.add('fa-sun');
    }

    // Notifications toggle
    if (notificationIcon && notificationsTab) {
        notificationIcon.addEventListener('click', function(event) {
            event.preventDefault();
            notificationsTab.classList.toggle('show-notifications');  // Toggle visibility of notifications tab
        });
    }

    // Dark Mode toggle
    if (modeIcon && body) {
        modeIcon.addEventListener('click', function(event) {
            event.preventDefault();
            body.classList.toggle('dark-mode');  // Toggle dark mode class

            // Save dark mode preference to localStorage
            if (body.classList.contains('dark-mode')) {
                localStorage.setItem('darkMode', 'enabled');  // Save dark mode enabled
                // modeIcon.querySelector('i').classList.remove('fa-moon');
                // modeIcon.querySelector('i').classList.add('fa-sun');
            } else {
                localStorage.setItem('darkMode', 'disabled');  // Save dark mode disabled
                // modeIcon.querySelector('i').classList.remove('fa-sun');
                // modeIcon.querySelector('i').classList.add('fa-moon');
            }
        });
    }
});


//stock-ticker section added at home
document.addEventListener("DOMContentLoaded", function () {
    const stockTickerText = document.getElementById("stock-ticker-text");

    // Sample stock data - You can replace this with dynamic data
    const stocks = [
        { symbol: "KSE 100", price: 6.95, change: -0.72 },
        { symbol: "ENERGY", price: 9.15, change: -0.36 },
        { symbol: "BOP", price: 3.98, change: -0.12 },
        { symbol: "KEL", price: 7.50, change: 0.35 },
    ];

    // Function to update the ticker text
    function updateTicker() {
        let tickerContent = "";
        stocks.forEach(stock => {
            tickerContent += `${stock.symbol}: $${stock.price} ${stock.change >= 0 ? '+' : ''}${stock.change} | `;
        });
        stockTickerText.textContent = tickerContent;
    }

    updateTicker();

    // Optionally, you can set a timer to refresh the stock prices every 10 seconds or so.
    setInterval(updateTicker, 10000);
});

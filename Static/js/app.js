document.addEventListener('DOMContentLoaded', function() {
    // =======================
    // Prediction Form Script
    // =======================
    const predictionForm    = document.getElementById('prediction-form');
    const stockTickerInput  = document.getElementById('stock-ticker');
    const tickerResult      = document.getElementById('ticker-result');
    const predictionPrice   = document.getElementById('prediction-price');
    const currentPrice      = document.getElementById('current-price');
    const loadingSpinner    = document.getElementById('loading-spinner');
    let   predictionChart;

    function getNextBusinessDay(date) {
        const d = new Date(date);
        do {
            d.setDate(d.getDate() + 1);
        } while (d.getDay() === 0 || d.getDay() === 6);
        return d;
    }

    if (predictionForm) {
        function clearResults() {
            tickerResult.textContent      = '-';
            predictionPrice.textContent   = '-';
            currentPrice.textContent      = 'Current Price: $-';
            const tbody = document.getElementById('prediction-table-body');
            if (tbody) tbody.innerHTML = '';
            const downloadInput = document.getElementById('download-ticker');
            if (downloadInput) downloadInput.value = '';
            currentPrice.style.display    = 'none';
            predictionPrice.style.display = 'none';
        }

        function showLoading() {
            loadingSpinner.style.display   = 'block';
            currentPrice.style.display     = 'none';
            predictionPrice.style.display  = 'none';
        }

        function hideLoading() {
            loadingSpinner.style.display   = 'none';
            currentPrice.style.display     = 'block';
            predictionPrice.style.display  = 'block';
        }

        function destroyChart() {
            if (predictionChart) predictionChart.destroy();
        }

        function renderChart(chartDataArray) {
            const ctx = document.getElementById('predictionChart').getContext('2d');
            const darkModeActive = document.body.classList.contains('dark-mode');

            const chartData = {
                labels: chartDataArray.map((_, i) => `Day ${i + 1}`),
                datasets: [{
                    label: 'Predicted Stock Price',
                    data: chartDataArray,
                    borderColor: '#1F8A70',
                    backgroundColor: 'rgba(31, 138, 112, 0.2)',
                    fill: true,
                    tension: 0.4
                }]
            };

            const chartOptions = {
                responsive: true,
                plugins: {
                    legend: { position: 'top', labels: { color: darkModeActive ? '#fff' : '#333' }},
                    tooltip: { mode: 'index', intersect: false }
                },
                scales: {
                    x: { 
                        ticks: { color: darkModeActive ? '#fff' : '#333' },
                        grid: { color: darkModeActive ? '#555' : '#ddd' }
                    },
                    y: { 
                        ticks: { color: darkModeActive ? '#fff' : '#333' },
                        grid: { color: darkModeActive ? '#555' : '#ddd' }
                    }
                }
            };

            destroyChart();

            predictionChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: chartOptions
            });
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

                if (!response.ok) throw new Error('Failed to fetch prediction data');
                const data = await response.json();
                if (data.error) throw new Error(data.error);

                const symbol = stockTicker.toUpperCase();
                tickerResult.textContent      = symbol;
                currentPrice.innerHTML        = `<strong>Current Price:</strong> $${data.current_price}`;
                predictionPrice.innerHTML     = `<strong>Predicted Price:</strong> $${data[1][0].toFixed(2)}`;

                const downloadInput = document.getElementById('download-ticker');
                if (downloadInput) downloadInput.value = symbol;

                const tbody = document.getElementById('prediction-table-body');
                tbody.innerHTML = '';
                let datePointer = new Date();

                data[30].forEach(price => {
                    datePointer = getNextBusinessDay(datePointer);
                    const tr      = document.createElement('tr');
                    const tdDate  = document.createElement('td');
                    const tdPrice = document.createElement('td');
                    tdDate.textContent  = datePointer.toLocaleDateString();
                    tdPrice.textContent = `$${price.toFixed(2)}`;
                    tr.appendChild(tdDate);
                    tr.appendChild(tdPrice);
                    tbody.appendChild(tr);
                });

                renderChart(data[30]);
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
    const slides       = document.querySelectorAll('.news-slide');
    let   currentIndex = 0;
    const slideCounter = document.getElementById('slideCounter');

    function updateCounter() {
        if (slideCounter) slideCounter.textContent = `${currentIndex + 1} / ${slides.length}`;
    }
    function showSlide(index) {
        slides.forEach((slide, i) => slide.classList.toggle('active', i === index));
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
    if (slides.length) {
        showSlide(currentIndex);
        updateCounter();
        setInterval(nextSlide, 4000);
        document.getElementById('nextSlide')?.addEventListener('click', nextSlide);
        document.getElementById('prevSlide')?.addEventListener('click', prevSlide);
    }

    // ========================
    // Notification & Dark Mode
    // ========================
    const notificationIcon = document.getElementById('notification-icon');
    const notificationsTab = document.getElementById('notifications-tab');
    const modeIcon         = document.getElementById('mode-icon');
    const body             = document.getElementById('body');

    if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
    }
    notificationIcon?.addEventListener('click', e => {
        e.preventDefault();
        notificationsTab.classList.toggle('show-notifications');
    });

    modeIcon?.addEventListener('click', e => {
        e.preventDefault();
        body.classList.toggle('dark-mode');
        localStorage.setItem('darkMode',
            body.classList.contains('dark-mode') ? 'enabled' : 'disabled'
        );

        // Also re-render chart if needed
        if (predictionChart && predictionChart.data) {
            renderChart(predictionChart.data.datasets[0].data);
        }
    });

    // ========================
    // Stock Ticker (Home)
    // ========================
    const stockTickerText = document.getElementById('stock-ticker-text');
    const stocks = [
        { symbol: "KSE 100", price: 6.95, change: -0.72 },
        { symbol: "ENERGY", price: 9.15, change: -0.36 },
        { symbol: "BOP",    price: 3.98, change: -0.12 },
        { symbol: "KEL",    price: 7.50, change:  0.35 },
    ];
    function updateTicker() {
        let text = "";
        stocks.forEach(s => {
            text += `${s.symbol}: $${s.price} ${s.change >= 0 ? '+' : ''}${s.change} | `;
        });
        if (stockTickerText) {
            stockTickerText.textContent = text;
        }
    }
    updateTicker();
    setInterval(updateTicker, 10000);
});

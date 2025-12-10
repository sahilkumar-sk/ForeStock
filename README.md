# ForeStock  
### *AI-Powered Stock Price Forecasting with Sentiment Analysis & Deep Learning*

ForeStock is a full-stack machine learning project that predicts future stock prices using an LSTM deep-learning model enhanced with technical indicators and real-time news sentiment.  
The app also includes a built-in GPT-powered chatbot that helps users understand market concepts.

---

## Features

### **LSTM Deep Learning Forecasting**
- Predicts **1-day**, **15-day**, and **30-day** stock prices  
- Uses a tuned **Bidirectional LSTM** architecture  
- Trained on multi-year historical data  
- Hyperparameter tuning with **Keras Tuner**

### **News Sentiment Analysis**
- Fetches real-time news via **NewsAPI**  
- Uses **TextBlob** to calculate sentiment polarity  
- Sentiment becomes an input signal for the ML model  

### **Technical Indicators Included**
Automatically calculates:
- 50-day & 200-day Moving Average  
- RSI  
- MACD  
- EMA  
- OHLCV features

### **Built-in Chatbot (GPT-2)**
- Answers finance-related questions  
- Uses HuggingFace Transformers  
- Context-aware, concise responses  

### **Flask Web Application**
- Interactive stock prediction UI  
- CSV export for 30-day forecasts  
- News page with sorting & deduplication  
- Trending stocks widget  

### **Automated Testing Suite**
Includes tests for:
- Preprocessing  
- Sentiment scoring  
- Model predictions  
- API data fetching  

---

## Tech Stack

| Layer     | Technologies |
|-----------|--------------|
| **Backend**   | Python, Flask, Keras, TensorFlow, yFinance, TextBlob, scikit-learn |
| **Frontend**  | HTML, CSS, JavaScript (Flask Jinja Templates) |
| **ML / AI**   | LSTM, Bidirectional LSTM, Keras Tuner, Sentiment Analysis |


---

## Project Structure

```
oreStock/
│
├── app.py
├── api_handler.py
├── chatbot.py
├── fetch_news.py
├── lstm_model.py
├── train_lstm_model.py
├── templates/
├── Static/
├── utils/
│ └── preprocessing.py
├── tests/
└── stock_prediction_model_with_tuned_hyperparameters.keras
```

---

##  Installation

### 1️ Clone the repository
```
git clone https://github.com/sahilkumar-sk/ForeStock.git
cd ForeStock
````

### 2️ Install dependencies

```
pip install -r requirements.txt
```

### 3️ Add your NewsAPI key

In `fetch_news.py` and `app.py`, replace:

```
api_key = "YOUR_NEWSAPI_KEY"
```

### 4️ Run the application

```
python app.py
```

---

## Model Training (Optional)

If you want to retrain or tune the LSTM model:

```bash
python train_lstm_model.py
```


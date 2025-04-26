from api_handler import get_stock_data
from utils.preprocessing import preprocess_data_with_sentiment, prepare_data
from keras.optimizers import Adam, AdamW
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.optimizers import RMSprop
from lstm_model import test_optimizers  # Import the optimizer testing function
import matplotlib.pyplot as plt
from config import stock_symbols
import pandas as pd
from keras.layers import Bidirectional


# Fetch and combine stock data for all symbols
all_data = []
for stock_symbol in stock_symbols:
    df = get_stock_data(stock_symbol, '3y')  # Fetch 5 years of data for each stock
    df['stock_symbol'] = stock_symbol  # Add a column to identify the stock
    all_data.append(df)

# Combine all stock data into a single DataFrame
combined_data = pd.concat(all_data, ignore_index=True)

# Preprocess the combined stock data and add sentiment as a feature
combined_data_scaled, scaler = preprocess_data_with_sentiment(
    combined_data, stock_symbol=None, api_key='6033221f384f4e4395d7410df82c3fdd'
)
X, y = prepare_data(combined_data_scaled, time_step=60)

# Split the data into training and validation sets (80% training, 20% validation)
train_size = int(len(X) * 0.8)
X_train, X_val = X[:train_size], X[train_size:]
y_train, y_val = y[:train_size], y[train_size:]

# Define the input shape for the model
input_shape = (X_train.shape[1], X_train.shape[2])

# Test different optimizers
optimizers = {
    "Adam": Adam(learning_rate=1e-3),
    "AdamW": AdamW(learning_rate=1e-3),
    "RMSprop": RMSprop(learning_rate=1e-3)
}
results = test_optimizers(input_shape, X_train, y_train, X_val, y_val, optimizers)
best_optimizer_name = min(results, key=lambda k: results[k]["MSE"])
best_optimizer = optimizers[best_optimizer_name]

# Save the optimizer testing results to a JSON file
import json
with open('optimizer_results.json', 'w') as f:
    json.dump(results, f)

# Select the best optimizer based on the results (e.g., lowest MSE)
best_optimizer_name = min(results, key=lambda k: results[k]["MSE"])
print(f"Best Optimizer: {best_optimizer_name} with MSE: {results[best_optimizer_name]['MSE']}")

# Use the best optimizer for training the final model
best_optimizer = optimizers[best_optimizer_name]

# Build and train the final model
model = Sequential()
model.add(Bidirectional(LSTM(64, return_sequences=True, input_shape=input_shape)))  # Bidirectional LSTM
model.add(Dropout(0.4))
model.add(LSTM(64, return_sequences=False))
model.add(Dropout(0.4))
model.add(Dense(1))
model.compile(optimizer=best_optimizer, loss='mse')

# Train the model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_data=(X_val, y_val))

# Save the trained model
model.save('stock_prediction_model_with_best_optimizer.keras')

# Plot training and validation loss
plt.plot(history.history['loss'], label='Training Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.title('Model Loss over Epochs')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()
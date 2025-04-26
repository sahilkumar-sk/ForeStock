from keras.callbacks import EarlyStopping, ReduceLROnPlateau
from kerastuner import HyperModel, RandomSearch
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout, Bidirectional
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define the hypermodel for Keras Tuner
class StockPredictor(HyperModel):
    def build(self, hp):
        model = Sequential([
            Bidirectional(LSTM(hp.Int('units', 64, 128, 32), return_sequences=True, input_shape=(60, 5))),
            Dropout(0.4),
            LSTM(hp.Int('units', 64, 128, 32)),
            Dropout(0.4),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=hp.Choice('learning_rate', [1e-3, 1e-4])), loss='mse')
        return model

# Callbacks
def get_callbacks():
    return [
        EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=1e-6)
    ]

# Plot training history
def plot_history(history):
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Model Loss over Epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()

# Train the model
def train_model(X_train, y_train, X_val, y_val):
    tuner = RandomSearch(
        StockPredictor(),
        objective='val_loss',
        max_trials=10,
        executions_per_trial=1,
        directory='tuner_results',
        project_name='stock_price_prediction'
    )
    tuner.search(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=32)
    best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    logging.info(f"Best hyperparameters: {best_hps.values}")
    best_model = tuner.hypermodel.build(best_hps)
    history = best_model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=50, batch_size=32, callbacks=get_callbacks())
    best_model.save('stock_prediction_model_with_tuned_hyperparameters.keras')
    plot_history(history)
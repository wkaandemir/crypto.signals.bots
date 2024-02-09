import os  # Module for system functions
import time  # For time-related operations
import requests  # For sending HTTP requests
from ta.momentum import RSIIndicator  # Using the RSIIndicator class from the TA library to calculate RSI
import pandas as pd  # For data analysis
import symbolsList  # Custom module containing symbols for trading

# Base URL for the Binance API
binance_api_url = "https://api.binance.com/api/v3"
# List of symbols for trading
symbols = symbolsList.symbols
# Lower threshold for RSI
rsi_lower_threshold = 30
# Time interval for candlestick data (e.g., 1m, 3m, 5m, 15m, 30m, 45m, 1h, 2h, 3h, 4h)
time_interval = "5m"

# Call the API to get candlestick data for a specific symbol
def get_candlestick_data(symbol, interval, limit):
    url = f"{binance_api_url}/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return data

# Show a sound alert when the RSI drops below 30
def sound_alert_lower():
    print("RSI dropped below 30! Alerting...\n \n ")
    os.system('afplay /System/Library/Sounds/Ping.aiff')  # Play system sound on macOS
    time.sleep(3)

# Check RSI for a specific symbol and alert if necessary
def check_rsi(symbol):
    candlestick_data = get_candlestick_data(symbol, time_interval, 100)  # Get candlestick data for a specific symbol
    closes = [float(entry[4]) for entry in candlestick_data]  # Get closing prices
    closes_series = pd.Series(closes)  # Create a Pandas Series
    rsi_indicator = RSIIndicator(close=closes_series)  # Create RSI indicator
    rsi = rsi_indicator.rsi().iloc[-1]  # Calculate RSI value
    print(f"{symbol:<15} RSI: {rsi:.2f}")  # Print RSI value
    if rsi < rsi_lower_threshold:  # Check if RSI is below the threshold
        sound_alert_lower()  # Show sound alert
        time.sleep(3)  # Short pause between alerts

# Main loop: Periodically check RSI for all symbols
def main():
    while True:
        for symbol in symbols:
            check_rsi(symbol)
        time.sleep(1)  # Wait for one second after each loop

# Execute the code
if __name__ == "__main__":
    main()

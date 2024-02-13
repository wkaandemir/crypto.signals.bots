import os  # Module for system functions
import time  # Module for time-related operations
import requests  # Module for sending HTTP requests
from ta.momentum import RSIIndicator  # Using the RSIIndicator class from the TA library to calculate RSI
import pandas as pd  # Module for data analysis
import symbolsList  # Custom module containing symbols for trading
import sys

# Base URL for the Binance API
binance_api_url = "https://api.binance.com/api/v3"
# List of symbols for trading
symbols = symbolsList.symbols
# Lower threshold for RSI
rsi_lower_threshold = 30
# Time intervals for candlestick data (e.g., 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h)
time_intervals = ["4h", "2h", "1h", "30m", "15m", "5m"]  # Updated list of time intervals

# Call API to get candlestick data for a specific symbol
def get_candlestick_data(symbol, interval, limit):
    url = f"{binance_api_url}/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    return data

# Sound an alert when RSI drops below 30
def audible_alert():
    if sys.platform.startswith('darwin'):  # macOS
        os.system('afplay /System/Library/Sounds/Ping.aiff')
    elif sys.platform.startswith('win32'):  # Windows
        import winsound
        winsound.Beep(1000, 200)  # Produces a beep sound in Windows

# Check RSI for a specific symbol and show alert if necessary
def check_rsi(symbol, interval):
    candlestick_data = get_candlestick_data(symbol, interval, 100)  # Get candlestick data for a specific symbol
    closes = [float(entry[4]) for entry in candlestick_data]  # Get closing prices
    closes_series = pd.Series(closes)  # Create a Pandas Series
    rsi_indicator = RSIIndicator(close=closes_series)  # Create an RSI indicator
    rsi = rsi_indicator.rsi().iloc[-1]  # Calculate RSI value
    print(f"{symbol:<15} RSI ({interval}): {rsi:.2f}")  # Print RSI value
    if rsi < rsi_lower_threshold:  # Check if RSI is below the threshold
        audible_alert()  # Sound alert
        time.sleep(1)  # Short pause between alerts

# Main loop: Regularly check RSI for all symbols
def main():
    for interval in time_intervals:  # Loop over the list of time intervals
        for symbol in symbols:
            check_rsi(symbol, interval)
            #time.sleep(1)  # Short pause between each symbol

# Run the code
if __name__ == "__main__":
    main()

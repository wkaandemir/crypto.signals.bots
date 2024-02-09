# Importing necessary libraries
from binance import Client  # Binance API client
import config  # Configuration file for API keys
import pandas as pd  # Data manipulation library
import os  # Operating system library for system-related functions

# Initialize the Binance client with API keys
client = Client(config.apiKey, config.secretKey)

# List of symbols for which historical data will be retrieved
symbolList = ["BTCUSDT"]  # You can add more symbols here, separated by commas  "XRPUSDT","BNBUSDT"

# Function to sound an alert when the data retrieval process is complete
def sound_alert():
    os.system('afplay /System/Library/Sounds/Ping.aiff')  # Plays a system sound (works on macOS)

# Function to write historical data to an Excel file
def historical_Data_Write(symbol, candlesticks, start_date, end_date):
    # Creating a DataFrame from the candlestick data
    df = pd.DataFrame(candlesticks, columns=["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"])
    # Converting timestamps to datetime format
    df['Open Time'] = pd.to_datetime(df['Open Time'], unit='ms')
    df['Close Time'] = pd.to_datetime(df['Close Time'], unit='ms')
    # Generating a filename based on symbol and date range
    filename = f"{symbol}_{start_date}_{end_date}.xlsx"
    # Writing the DataFrame to an Excel file
    df.to_excel(filename, index=False)

# Loop through each symbol in the symbol list and retrieve historical data
for symbol in symbolList:
    # Define start and end dates for data retrieval
    start_date = "2023-01-01"  # Start date
    end_date = "2024-01-30"  # End date
    print("DATA RETRIEVAL: ", symbol)
    # Retrieve historical candlestick data from Binance API
    candlesticks = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1HOUR, start_date, end_date)
    # Write the retrieved data to an Excel file
    historical_Data_Write(symbol, candlesticks, start_date, end_date)

# Sound alert to indicate that data retrieval process is complete
sound_alert()
print("Data retrieval process complete. Check Excel files.")

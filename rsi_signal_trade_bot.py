from ta.momentum import RSIIndicator  # Importing RSIIndicator from TA library for momentum calculation
import ccxt  # Importing ccxt for cryptocurrency exchange interaction
import pandas as pd  # Importing pandas for data manipulation
import time  # Importing time for time-related operations
import os  # Importing os for system operations
import config  # Importing configuration file (presumably containing API keys)
import warnings  # Importing warnings to suppress unwanted warnings
import symbols_list  # Importing symbols_list which presumably contains a list of symbols to trade

# Suppress warnings
warnings.filterwarnings("ignore")

# Function to play a sound alert
def sound_alert_lower():
    print("RSI dropped below 30! Alerting...")
    os.system('afplay /System/Library/Sounds/Ping.aiff')  # Playing an alert sound

# Function to enter long position
def longEnter(symbol, amount, exchange):
    order = exchange.create_market_buy_order(symbol, amount)  # Creating a market buy order
    sound_alert_lower()  # Calling the sound alert function

# Function to exit long position
def longExit(symbol, position_amount, exchange):
    order = exchange.create_market_sell_order(symbol, position_amount, {"reduceOnly": True})  # Creating a market sell order
    sound_alert_lower()  # Calling the sound alert function

# Function to get user input for trading parameters
def get_trading_parameters():
    islemeGirecekPara = float(input("Enter the amount you want to invest: "))  # Getting investment amount
    leverage = float(input("Enter the leverage: "))  # Getting leverage
    stopLoss = input("StopLoss %: ")  # Getting stop loss percentage
    return islemeGirecekPara, leverage, stopLoss  # Returning trading parameters

# Main function to execute trading strategy
def ana(symbol):
    # Get trading parameters from user
    islemeGirecekPara, leverage, stopLoss = get_trading_parameters()

    # Connect to the exchange
    exchange = ccxt.binance({
        "apiKey": config.apiKey,  # API Key
        "secret": config.secretKey,  # Secret Key
        'options': {'defaultType': 'future'},  # Setting default exchange type
        'enableRateLimit': True  # Enabling rate limit
    })

    # Fetch balance and position information
    balance = exchange.fetch_balance()  # Fetching account balance
    free_balance = exchange.fetch_free_balance()  # Fetching free balance
    positions = balance['info']['positions']  # Fetching position information
    newSymbol = symbol + "USDT"  # Appending USDT to symbol
    current_positions = [position for position in positions if float(position['positionAmt']) != 0 and position['symbol'] == newSymbol]  # Filtering current positions
    position_info = pd.DataFrame(current_positions, columns=["symbol", "entryPrice", "unrealizedProfit", "isolatedWallet", "positionAmt", "positionSide"])  # Creating DataFrame for position info

    # Check if there is an open position
    if not position_info.empty and float(position_info["positionAmt"][len(position_info.index) - 1]) != 0:
        has_position = True
    else:
        has_position = False

    # Check if it's a long position
    if not position_info.empty and float(position_info["positionAmt"][len(position_info.index) - 1]) > 0:
        is_long_position = True
    else:
        is_long_position = False

    # Fetch OHLCV data
    bars = exchange.fetch_ohlcv(symbol, timeframe="1m", since=None, limit=1500)  # Fetching OHLCV data
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])  # Creating DataFrame for OHLCV data

    # Calculate RSI
    rsi = RSIIndicator(df["close"], 14)  # Calculating RSI
    df["rsi"] = rsi.rsi()  # Adding RSI to DataFrame

    # Trading logic
    if not is_long_position and float(df["rsi"][len(df.index) - 2]) <= 30:  # If not in a long position and RSI is below or equal to 30
        # Define the amount to invest
        amount_to_invest = (float(free_balance["USDT"]) / 100) * islemeGirecekPara * leverage / float(df["close"][len(df.index) - 1])  # Calculating amount to invest
        print("Entering LONG position...")  # Printing message
        longEnter(symbol, amount_to_invest, exchange)  # Calling function to enter long position

    # Stop Loss
    if is_long_position and ((float(df["close"][len(df.index) - 1]) - float(position_info["entryPrice"][len(position_info.index) - 1])) / float(position_info["entryPrice"][len(position_info.index) - 1])) * 100 * -1 >= float(stopLoss):  # If in long position and stop loss condition met
        print("Exiting LONG position due to Stop Loss...")  # Printing message
        longExit(symbol, float(position_info["positionAmt"][len(position_info.index) - 1]), exchange)  # Calling function to exit long position

    time.sleep(2)  # Pause execution for 2 seconds

if __name__ == "__main__":
    symbols = symbols_list.symbols  # Getting symbols to trade
    while True:  # Infinite loop for continuous trading
        for symbol in symbols:  # Iterating through symbols
            ana(symbol)  # Calling main trading function for each symbol

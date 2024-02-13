from ta.momentum import RSIIndicator  # Importing RSI indicator from the ta library
import ccxt  # Importing the ccxt library for cryptocurrency exchange integration
import pandas as pd  # Importing pandas for data manipulation
import time  # Importing time for time-related operations
import config  # Importing a config file (presumably containing API keys)
import warnings  # Importing warnings to suppress unnecessary warnings
import symbolsList  # Importing a list of symbols to trade
import os  # Importing os for system-related operations
import sys

warnings.filterwarnings("ignore")  # Ignoring warnings

# Function to get trading parameters
def get_trading_parameters():
    rsi_threshold = 30  # RSI threshold for triggering trades
    profit_rate = 1.01  # Profit rate to sell at
    leverage = 5  # Leverage used for trading
    amount_to_trade = 10  # Amount to trade (in USDT)
    stop_loss = 0.50  # Stop loss percentage
    return amount_to_trade, leverage, stop_loss, rsi_threshold, profit_rate

# Function to play a sound alert
def audible_alert():
    if sys.platform.startswith('darwin'):  # macOS
        os.system('afplay /System/Library/Sounds/Ping.aiff')
    elif sys.platform.startswith('win32'):  # Windows
        import winsound
        winsound.Beep(1000, 200)  # Produces a beep sound in Windows

# Function to execute a long position entry
def long_enter(symbol, amount, exchange):
    order = exchange.create_market_buy_order(symbol, amount)  # Creating a market buy order
    audible_alert()  # Playing a sound alert

# Function to execute a long position exit
def long_exit(symbol, position_amount, exchange):
    order = exchange.create_market_sell_order(symbol, position_amount, {"reduceOnly": True})  # Creating a market sell order with "reduceOnly" option
    audible_alert()  # Playing a sound alert

# Function to check the RSI of a symbol
def rsi_check(symbol, exchange):
    bars = exchange.fetch_ohlcv(symbol, timeframe="4h", since=None, limit=100)  # Fetching OHLCV data for the symbol
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])  # Converting OHLCV data to a DataFrame
    rsi = RSIIndicator(df["close"], 14)  # Calculating RSI with a period of 14
    rsi_result = rsi.rsi().iloc[-1]  # Getting the last RSI value
    return rsi_result

# Function to get the current price of a symbol
def get_price(symbol, exchange):
    bars = exchange.fetch_ohlcv(symbol, timeframe="1m", since=None, limit=100)  # Fetching OHLCV data for the symbol
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])  # Converting OHLCV data to a DataFrame
    current_price = df['close']  # Getting the close price
    buy_sell_price = current_price.iloc[-1]  # Getting the last close price
    return buy_sell_price

# Main trading logic
def main(symbol, amount_to_trade, leverage, stop_loss, exchange, rsi_threshold, profit_rate):
    bars = exchange.fetch_ohlcv(symbol, timeframe="1m", since=None, limit=100)  # Fetching OHLCV data for the symbol
    df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])  # Converting OHLCV data to a DataFrame
    balance = exchange.fetch_free_balance()  # Fetching the free balance from the exchange
    if rsi_check(symbol, exchange) is not None:  # Checking if RSI is calculated successfully
        print(f"RSI for {symbol:<15}: {rsi_check(symbol, exchange):.2f}")  # Printing the RSI value
        if rsi_check(symbol, exchange) < rsi_threshold:  # Checking if RSI is below the threshold
            start_price = get_price(symbol,exchange)  # Getting the start price for the symbol
            print(f"Start price: {start_price} - Symbol: {symbol}")  # Printing start price and symbol
            amount = (((float(balance["USDT"]) / 100 ) * float(amount_to_trade)) * float(leverage)) / float(df["close"][len(df.index) - 1])  # Calculating the amount to trade
            long_enter(symbol, amount, exchange)  # Executing long position entry
            while True:  # Looping until exit conditions are met
                current_price = get_price(symbol,exchange)  # Getting the current price
                print(f"{symbol} Purchase Price: {start_price:.4f} - Current Price: {current_price:.4f} - Stop Price: {(start_price * stop_loss):.4f} - Profit Price: {(start_price * profit_rate):.4f}")  # Printing price info
                if current_price > start_price * profit_rate:  # Checking for profit target
                    long_exit(symbol, amount, exchange)  # Exiting position
                    break
                elif current_price < start_price * stop_loss:  # Checking for stop loss
                    long_exit(symbol, amount, exchange)  # Exiting position
                    break
                time.sleep(2)  # Adding a delay to prevent rate limiting

# Entry point of the program
if __name__ == "__main__":
    symbols = symbolsList.symbols  # Getting symbols to trade from symbolsList module
    amount_to_trade, leverage, stop_loss, rsi_threshold, profit_rate = get_trading_parameters()  # Getting trading parameters
    exchange = ccxt.binance({  # Creating a Binance exchange instance
        "apiKey": config.apiKey,
        "secret": config.secretKey,
        'options': {'defaultType': 'future'},
        'enableRateLimit': True
    })

    while True:  # Main trading loop
        for symbol in symbols:  # Iterating over symbols
            main(symbol, amount_to_trade, leverage, stop_loss, exchange, rsi_threshold, profit_rate)  # Calling the main trading logic
            time.sleep(1)  # Adding a delay to prevent rate limiting

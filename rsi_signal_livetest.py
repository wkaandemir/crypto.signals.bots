import requests  # Used for making HTTP requests.
from ta.momentum import RSIIndicator  # Library containing portable technical analysis functions.
import time  # Used for time-related operations.
import pandas as pd  # Used for data analysis.
import symbolsList  # Imports symbols list from another file for trading.

# Function to get the current price of a specific symbol.
def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}"
        response = requests.get(url)  # Fetches data from the specified URL.
        response.raise_for_status()  # Raises an exception in case of any HTTP error.
        data = response.json()  # Converts the response to JSON format.
        current_price = float(data['price'])  # Extracts the price from JSON and converts it to a float.
        return current_price
    except Exception as e:  # Raises an exception in case of any error.
        print(f"An error occurred: {e}")  # Prints the error message.
        return None  # Returns None in case of an error.

# Function to check RSI (Relative Strength Index) for a specific symbol.
def rsi_check(symbol):
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1m&limit=100"
        response = requests.get(url)  # Fetches data from the specified URL.
        response.raise_for_status()  # Raises an exception in case of any HTTP error.
        data = response.json()  # Converts the response to JSON format.

        # Collects closing prices in a list.
        closings = [float(entry[4]) for entry in data]
        closing_series = pd.Series(closings)  # Converts closings to a pandas Series.
        rsi_indicator = RSIIndicator(close=closing_series)  # Creates an RSI indicator.
        rsi_value = rsi_indicator.rsi().iloc[-1]  # Gets the last RSI value.
        return rsi_value
    except Exception as e:  # Raises an exception in case of any error.
        print(f"An error occurred: {e}")  # Prints the error message.
        return None  # Returns None in case of an error.

wallet_amount = 3000  # Initial wallet amount.
total_profit = 0  # Total profit amount.
profit_rate = 1.001  # Profit rate (e.g., 0.1%).
commission_rate = 0.0004  # Commission rate (0.04%).

# Main function
def main(symbol):
    global wallet_amount, total_profit  # Uses global variables.

    rsi_threshold = 30  # Threshold value for RSI for buying.
    stop_loss_rate = 0.95  # Stop-loss level (5% loss).

    rsi = rsi_check(symbol)  # Checks RSI.
    if rsi is not None:  # Proceeds if RSI value is not empty.
        print(f"RSI for {symbol:<10}: {rsi:.2f}")  # Prints RSI value for the symbol.
        if rsi < rsi_threshold:  # Buys if RSI is below the threshold.
            start_price = get_price(symbol)  # Gets the initial price.
            current_price = start_price  # Sets initial price as the current price.
            if current_price <= start_price:  # Executes if the price is less than or equal to the initial price.
                spent_amount = wallet_amount * 0.01  # Calculates the amount spent.
                bought_amount = spent_amount / start_price  # Calculates the amount bought.
                wallet_amount -= spent_amount  # Deducts spent amount from wallet.
                remaining_amount = wallet_amount - spent_amount  # Calculates remaining amount.
                print(f"- Wallet: {wallet_amount:<9.3f} - Bought {symbol}   ")  # Prints buy info.
                while True:  # Initiates an infinite loop.
                    current_price = get_price(symbol)  # Gets the current price.
                    print(f"{symbol} Purchase Price: {start_price:.4f} - Current Price: {current_price:.4f} - Stop Price: {(start_price * stop_loss_rate):.4f} - Profit Price: {(start_price * profit_rate):.4f}")  # Prints price info.
                    if current_price > start_price * profit_rate:  # Condition for taking profit.
                        earned_amount = bought_amount * current_price  # Calculates the amount earned.
                        commission_amount = earned_amount * commission_rate  # Calculates commission amount.
                        wallet_amount += earned_amount - commission_amount  # Updates wallet amount.
                        profit = ((earned_amount - spent_amount) * bought_amount) - (commission_amount * bought_amount)  # Calculates profit.
                        total_profit += profit  # Updates total profit.
                        remaining_amount = wallet_amount + total_profit  # Calculates remaining amount.
                        with open("test_log.txt", "a") as file:  # Writes transaction info to a log file.
                            line = f"- Wallet: {remaining_amount:<9.3f} - Purchase Price for {symbol:<6}: {start_price:<9.4f} - Amount Bought: {bought_amount:<9.4f} - Current Price: {current_price:<9.4f} - Total Profit: {total_profit:<9.3f} - Profit: {profit:<9.4f} - Spent Amount: {spent_amount:.4f} - Commission: {commission_amount:.4f}\n"  # Creates the line to be written.
                            print(line, end="")  # Prints the line.
                            file.write(line)  # Writes the line to the log file.
                        break  # Exits the loop.
                    elif current_price < start_price * stop_loss_rate:  # Condition for stop-loss.
                        sold_amount = bought_amount * stop_loss_rate  # Calculates the amount sold.
                        commission_amount = sold_amount * current_price * commission_rate  # Calculates commission amount.
                        wallet_amount += sold_amount * current_price - commission_amount  # Updates wallet amount.
                        print(f"- Wallet: {wallet_amount:<9.3f} - {symbol} Sold (Stop-loss)  ")  # Prints sell info.
                        print(f"Commission: {commission_amount:.3f}")  # Prints commission info.
                        break  # Exits the loop.
                    time.sleep(1)  # Waits for one second.

    time.sleep(1)  # Waits for one second.

# Runs the main function.
if __name__ == "__main__":
    while True:  # Initiates an infinite loop.
        for symbol in symbolsList.symbols:  # Calls the main function for each symbol in symbols_list.
            main(symbol)

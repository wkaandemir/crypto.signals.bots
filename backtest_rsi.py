from ta.momentum import RSIIndicator
import pandas as pd
import os

# Function to play system alert sound
def sound_alert():
    os.system('afplay /System/Library/Sounds/Ping.aiff')

# Function to backtest RSI strategy
def backtest_rsi_strategy(df, rsi_period=14, rsi_lower=30):
    # Initial trade state and fundamental variable values
    in_trade = False
    initial_capital = 100
    trade_count = 0
    win = 0
    loss = 0
    lowest_capital = initial_capital
    highest_capital = initial_capital
    win_rate = 0
    entry_signal_time = 0

    # Calculating RSI indicator
    rsi_indicator = RSIIndicator(close=df["Close"], window=rsi_period)
    df["RSI"] = rsi_indicator.rsi()

    # Iterating through each time step
    for i in range(df.shape[0]):
        # Skipping the first rsi_period data points
        if i > rsi_period:
            # Buying signal when RSI is below the specified lower bound
            if df["RSI"][i-1] < rsi_lower:
                if not in_trade and initial_capital > 0:
                    open_price = df["Open"][i]
                    in_trade = True
                    entry_signal_time = df["Open Time"][i]
                    print("Buy signal - RSI:", int(df["RSI"][i-1]), "Bought Price:", open_price)
            # Selling when a certain profit target is reached after buying
            elif in_trade and df["Open"][i] > open_price * 1.01:  
                sell_price = df["Open"][i]
                initial_capital *= (sell_price / open_price - 0.001)  
                if initial_capital < lowest_capital:
                    lowest_capital = initial_capital
                trade_count += 1
                win += 1
                win_rate = (win / trade_count) * 100
                in_trade = False
                print("Profit target reached - RSI:", int(df["RSI"][i-1]), "Sold Price:", sell_price)
                time_diff_seconds = (df["Open Time"][i] - entry_signal_time).total_seconds()
                time_diff_hours = time_diff_seconds / 3600
                print("Time between buy signal and sell signal:", round(time_diff_hours, 2), "hours")

    # Printing backtest results
    print("BACKTEST FINISHED. RESULTS: ")
    print("Total Capital: ", initial_capital)
    print("Lowest Capital: ", lowest_capital)
    print("Highest Capital: ", highest_capital)
    print("Completed Trades: ", trade_count)
    print("Win: ", win, " Loss: ", loss, " Win Rate: ", win_rate)

# Reading Excel file
xlsx_name = "BTCUSDT_2023-01-01_2024-01-30.xlsx"
# Column names in the Excel file
attributes = ["Open Time", "Open", "High", "Low", "Close", "Volume", "Close Time", "Quote Asset Volume", "Number of Trades", "Taker Buy Base Asset Volume", "Taker Buy Quote Asset Volume", "Ignore"]
# Loading Excel data into DataFrame
df = pd.read_excel(xlsx_name)

# Calling the function to backtest RSI strategy
backtest_rsi_strategy(df)
# Sound alert
sound_alert()

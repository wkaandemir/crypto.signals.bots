import requests  # For making HTTP requests
import json      # For processing JSON data

# Binance API URL
url = "https://api.binance.com/api/v3/ticker/24hr"

# Fetch data from the API
response = requests.get(url)

# Convert JSON data to Python dictionaries
data = json.loads(response.text)

# Create a list to hold cryptocurrencies traded with USDT
coins = []

# Loop through the list of all cryptocurrencies
for ticker in data:
    # If the symbol ends with USDT
    if ticker["symbol"].endswith("USDT"):
        # Add the symbol and trading volume (quoteVolume) to the list
        coins.append((ticker["symbol"], float(ticker["quoteVolume"])))

# Sort cryptocurrencies by trading volume in descending order
coins.sort(key=lambda x: x[1], reverse=True)

# Get symbols of the top 50 cryptocurrencies
top_100_coins = coins[:50]

# Save symbols to a Python file
with open("symbolsList.py", "w") as f:
    f.write("symbols = [")  # Start the list
    for coin in top_100_coins:
        f.write("\"" + coin[0] + "\",\n")  # Add each symbol to the file
    f.write("]")  # Close the list

# Inform the user
print("Top 50 cryptocurrencies by market volume have been saved to symbolsList.py file!")

import numpy as np
from binance.client import Client
from stable_baselines3 import PPO
import time
import signal
import sys

# Binance.US API credentials 
api_key = 'INSERT YOUR OWN BINANCE API KEY HERE'
api_secret = 'INSERT YOUR OWN BINANCE API KEY HERE'

# Initialize the Binance client for real-time data
client = Client(api_key, api_secret, tld='us')

# Load the trained PPO model
model = PPO.load("ppo_trading_model_with_short")

# Function to fetch real-time market data (BTC/USDT)
def get_real_time_data(symbol):
    try:
        # Fetch the latest kline (candlestick) data
        kline = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
        
        close_price = float(kline[0][4])  # Closing price of the latest candle
        volume = float(kline[0][5])  # Volume during the latest candle

        # Fetch 1-hour high and low (rolling)
        klines_1h = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=60)
        high_1h = max([float(k[2]) for k in klines_1h])  # Highest high in the last 60 minutes
        low_1h = min([float(k[3]) for k in klines_1h])  # Lowest low in the last 60 minutes

        # Calculate VWAP, handle division by zero
        vwap = (close_price * volume) / volume if volume != 0 else close_price  # Simplified VWAP

        return np.array([close_price, volume, high_1h, low_1h, vwap])
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

# Manual termination handler
def signal_handler(sig, frame):
    print('Terminating the program...')
    sys.exit(0)

# Register the signal handler for manual termination (CTRL+C)
signal.signal(signal.SIGINT, signal_handler)

# User-specified initial balance
initial_balance = float(input("Enter the starting balance (USD): "))
balance = initial_balance
positions = 0.0  # Start with no BTC position

# Real-time paper trading loop with failure detection
previous_price = None
min_trade_size = 0.01  # Smallest trade size for BTC/USDT (0.01 BTC)
commission_rate = 0.001  # Example commission rate of 0.1%

while True:
    try:
        # Fetch real-time BTC price and other indicators
        state = get_real_time_data('BTCUSDT')
        if state is None:
            time.sleep(60)
            continue  # Skip if there's an issue with data fetching

        # Set initial previous price if this is the first iteration
        if previous_price is None:
            previous_price = state[0]

        # Predict action using the trained model (0: Hold, 1: Buy, 2: Sell, 3: Close)
        action, _ = model.predict(state)

        # Calculate trade costs and profit based on position size
        trade_cost = min_trade_size * state[0]  # Trade cost in USD for 0.01 BTC

        # Simulate trade and update balance/positions
        if action == 1:  # Buy (go long)
            if balance >= trade_cost * (1 + commission_rate):  # Ensure enough balance
                positions += min_trade_size
                balance -= trade_cost * (1 + commission_rate)  # Deduct trade cost and commission
                print(f"Buy 0.01 BTC at {state[0]}, Balance: {balance}, Positions: {positions} BTC")
            else:
                print("Not enough balance to buy.")

        elif action == 2:  # Sell (short)
            if positions >= min_trade_size:  # Ensure enough BTC to sell
                positions -= min_trade_size
                balance += trade_cost * (1 - commission_rate)  # Add trade cost minus commission
                print(f"Sell 0.01 BTC at {state[0]}, Balance: {balance}, Positions: {positions} BTC")
            else:
                print("Not enough position to sell.")

        elif action == 3 and positions != 0:  # Close position
            profit = (state[0] - previous_price) * positions  # Calculate profit
            balance += profit  # Add profit to the balance
            positions = 0  # Reset positions
            print(f"Close position at {state[0]}, Profit: {profit}, Balance: {balance}")

        # Detect failure: If the bot's balance drops below the initial investment
        if balance < 0:
            print(f"Failure detected! Balance: {balance}. Resetting to initial balance.")
            balance = initial_balance  # Reset balance
            positions = 0  # Clear any open positions
            previous_price = None  # Reset previous price

        # Update previous price for the next iteration
        previous_price = state[0]

        # Sleep for 1 minute before the next tick
        time.sleep(60)

    except Exception as e:
        print(f"Error: {e}")
        time.sleep(5)  # Wait for 5 seconds and try again to handle API issues

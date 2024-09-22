# AUTOMATICAI
# Crypto Trading Bot with Reinforcement Learning

This repository contains scripts to fetch historical cryptocurrency data, train a reinforcement learning model with shorting capabilities, and deploy a trading bot using the trained model.

## Files

- `fetch_historical_data.py`: Script to fetch and save historical cryptocurrency data from an exchange.
- `train_model_with_shorting.py`: Script to train a reinforcement learning model using the PPO algorithm with shorting capabilities.
- `reinforcement_learning_trader.py`: Script to deploy the trained model for real-time trading.

## Requirements

- Python 3.6+
- `pandas` library
- `gym` library
- `numpy` library
- `stable-baselines3` library
- `binance` library (for fetching real-time data)

You can install the required libraries using pip:

```bash
pip install pandas gym numpy stable-baselines3 binance

Usage
1. Fetch Historical Data
Use the fetch_historical_data.py script to fetch historical cryptocurrency data and save it to a CSV file.

2. Train the Model
Use the train_model_with_shorting.py script to train a reinforcement learning model with shorting capabilities.

This script includes:

Loading historical data from btc_historical_data.csv.
Defining a custom trading environment with actions for holding, buying, selling, and closing positions.
Training a PPO model using the custom environment.
3. Deploy the Trading Bot
Use the reinforcement_learning_trader.py script to deploy the trained model for real-time trading.

This script includes:

Initializing the Binance client.
Loading the trained PPO model.
Fetching real-time market data.
Making trading decisions based on the model.
Logging trades to trade_log.csv.
Disclaimer
This trading bot is for educational purposes only. Trading cryptocurrencies involves significant risk and can result in substantial financial losses. Use this bot at your own risk.

License
This project is unilcenced

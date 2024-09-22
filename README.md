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

import pandas as pd
import gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

# Load historical data (ensure that it's correctly formatted and clean)
data = pd.read_csv('btc_historical_data.csv')

# Define a custom trading environment
class TradingEnv(gym.Env):
    def __init__(self, data, initial_balance=10000):
        super(TradingEnv, self).__init__()
        self.data = data
        self.current_step = 0
        self.balance = initial_balance
        self.initial_balance = initial_balance
        self.positions = 0
        self.total_profit = 0
        self.transaction_cost = 0.001

        # Define action and observation space
        # Actions: 0 = Hold, 1 = Buy (go long), 2 = Sell (go short), 3 = Close position
        self.action_space = gym.spaces.Discrete(4)

        # Observations: Price, Volume, and other indicators (VWAP, highs/lows)
        self.observation_space = gym.spaces.Box(low=0, high=np.inf, shape=(5,))

    def reset(self):
        self.current_step = 0
        self.balance = self.initial_balance
        self.positions = 0
        self.total_profit = 0
        return self._next_observation()

    def _next_observation(self):
        try:
            # Get current price and volume
            price = self.data['Close'].iloc[self.current_step]
            volume = self.data['Volume'].iloc[self.current_step]

            # Handle rolling window data safely
            if self.current_step < 60:
                high_1h = self.data['High'].iloc[:self.current_step + 1].max()  # Fallback to max so far
                low_1h = self.data['Low'].iloc[:self.current_step + 1].min()    # Fallback to min so far
            else:
                high_1h = self.data['High'].rolling(window=60).max().iloc[self.current_step]  # 1 hour high
                low_1h = self.data['Low'].rolling(window=60).min().iloc[self.current_step]   # 1 hour low

            # Calculate VWAP (ensure cumulative sums aren't NaN)
            cum_volume = self.data['Volume'][:self.current_step + 1].cumsum()
            cum_price_vol = (self.data['Close'][:self.current_step + 1] * self.data['Volume'][:self.current_step + 1]).cumsum()
            
            # Fallback to price itself if not enough data for VWAP
            if cum_volume.iloc[-1] != 0:
                vwap = cum_price_vol.iloc[-1] / cum_volume.iloc[-1]
            else:
                vwap = price

            # Ensure no NaN or invalid values are returned in observations
            if np.isnan([price, volume, high_1h, low_1h, vwap]).any():
                raise ValueError("NaN value encountered in observation.")

            return np.array([price, volume, high_1h, low_1h, vwap])

        except Exception as e:
            print(f"Error generating observation: {e}")
            return np.array([0, 0, 0, 0, 0])  # Return default values to avoid NaNs

    def step(self, action):
        current_price = self.data['Close'].iloc[self.current_step]
        reward = 0
        profit = 0

        # Implement trading logic for buying, selling, and closing positions
        if action == 1:  # Buy (go long)
            self.positions += 1
            self.balance -= current_price * (1 + self.transaction_cost)

        elif action == 2:  # Sell (go short)
            self.positions -= 1
            self.balance += current_price * (1 - self.transaction_cost)

        elif action == 3 and self.positions != 0:  # Close position
            profit = (current_price - self.data['Close'].iloc[self.current_step - 1]) * self.positions
            self.balance += profit
            self.positions = 0

        self.total_profit += profit
        reward = profit

        # Reward for account profitability
        if self.balance > self.initial_balance:
            reward += 0.01 * (self.balance - self.initial_balance)

        # Ensure reward is a valid number
        if np.isnan(reward) or np.isinf(reward):
            reward = 0

        self.current_step += 1
        done = self.current_step >= len(self.data) - 1
        obs = self._next_observation()
        return obs, reward, done, {}

# Initialize the environment
env = DummyVecEnv([lambda: TradingEnv(data)])

# Create PPO model
model = PPO('MlpPolicy', env, verbose=1)

# Train the model
model.learn(total_timesteps=10000)

# Save the trained model
model.save("ppo_trading_model")

import time
import pandas as pd
from binance.client import Client
from datetime import datetime
from tqdm import tqdm  # For progress bar

# Binance.US API credentials 
api_key = 'INSERT YOUR OWN BINANCE API KEY HERE'
api_secret = 'INSERT YOUR OWN BINANCE API KEY HERE'

# Initialize the Binance client for fetching data
client = Client(api_key, api_secret, tld='us')

# Function to fetch historical data for a given symbol in chunks
def fetch_historical_data(symbol, interval, start_str, end_str=None):
    all_klines = []
    limit = 1000  # Maximum limit per request (Binance's limit is 1000)
    max_retry_attempts = 5  # To avoid endless retries in case of errors

    # Convert start_str and end_str into timestamp for progress tracking
    start_ts = int(pd.to_datetime(start_str).timestamp() * 1000)  # Convert to milliseconds
    if end_str:
        end_ts = int(pd.to_datetime(end_str).timestamp() * 1000)  # Convert to milliseconds
    else:
        end_ts = int(time.time() * 1000)  # Default end time: present

    total_data_points = (end_ts - start_ts) // (60 * 1000)  # 1-minute interval
    print(f"Fetching data from {start_str} to present (~{total_data_points} 1-minute intervals)")

    # Progress bar setup
    pbar = tqdm(total=total_data_points, desc="Fetching historical data", unit=" data points")

    while start_ts < end_ts:
        try:
            # Fetch a chunk of data (1000 rows at a time)
            klines = client.get_klines(symbol=symbol, interval=interval, limit=limit, startTime=start_ts, endTime=end_ts)

            if not klines:
                break  # Exit loop if no more data is returned

            all_klines.extend(klines)
            
            # Update start_ts to the timestamp of the last fetched kline for pagination
            last_kline_time = klines[-1][0]  # The first element is the timestamp
            start_ts = last_kline_time + 1  # Move to the next timestamp
            
            # Update the progress bar
            pbar.update(len(klines))

            # Respect the API rate limit (avoid hitting the rate limit by sleeping)
            time.sleep(0.5)  # Sleep for 500ms between requests for efficiency

        except Exception as e:
            print(f"Error fetching data: {e}")
            max_retry_attempts -= 1
            if max_retry_attempts == 0:
                print("Max retries reached, aborting data fetch.")
                break
            print(f"Retrying... {max_retry_attempts} attempts left.")
            time.sleep(1)  # Wait for 1 second before retrying
    
    pbar.close()

    # Convert the klines into a pandas DataFrame
    data = pd.DataFrame(all_klines, columns=[
        'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
        'Close_time', 'Quote_asset_volume', 'Number_of_trades',
        'Taker_buy_base_asset_volume', 'Taker_buy_quote_asset_volume', 'Ignore'
    ])

    # Convert prices and volume to numeric values
    data['Open'] = pd.to_numeric(data['Open'])
    data['High'] = pd.to_numeric(data['High'])
    data['Low'] = pd.to_numeric(data['Low'])
    data['Close'] = pd.to_numeric(data['Close'])
    data['Volume'] = pd.to_numeric(data['Volume'])

    return data

# Fetch historical BTC/USDT data in chunks (1-minute interval) from January 2021 up to the present
btc_data = fetch_historical_data('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, "1 Jan, 2021")

# Save the data to a CSV file
btc_data.to_csv('btc_historical_data.csv', index=False)
print("Data fetching complete. Saved to btc_historical_data.csv.")

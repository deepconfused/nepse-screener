# engine.py

import requests
import pandas as pd
import pandas_ta as ta # This is the technical analysis library

# We will start by screening a small list of stocks for faster testing.
# We can expand this list to all stocks later.
STOCKS_TO_SCREEN = ['NABIL', 'NTC', 'HDL', 'API', 'SHIVM', 'UPPER']

def get_historical_data(symbol, days=365):
    """Fetches historical data for a given stock symbol."""
    try:
        url = f"https://nepalipaisa.com/api/GetCompanyHistory?symbol={symbol}&range={days}"
        response = requests.get(url, timeout=10) # Added a timeout for safety
        response.raise_for_status() # Raise an error for bad responses (4xx or 5xx)
        
        data = response.json()
        
        if not data:
            print(f"Warning: No data returned for {symbol}")
            return None
            
        # Convert the list of dictionaries to a Pandas DataFrame
        df = pd.DataFrame(data)
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def analyze_stock(df):
    """Runs all technical analysis checks on a stock's data."""
    if df is None or len(df) < 20: # Need at least 20 days for reliable calculations
        return False

    # --- Data Preparation ---
    # Convert columns to the correct data types
    df['Date'] = pd.to_datetime(df['Date'])
    # Use 'coerce' to turn any non-numeric values into NaN (Not a Number)
    numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Drop any rows that had conversion errors
    df.dropna(inplace=True)
    df.set_index('Date', inplace=True) # Set Date as the index for time-series analysis
    df.sort_index(inplace=True) # Ensure data is in chronological order

    # --- 1. Calculate RSI ---
    # The 'append=True' argument adds the RSI data as a new column to our DataFrame
    df.ta.rsi(length=14, append=True)
    
    # --- 2. Calculate 5-day Average Volume ---
    df['Volume_5d_avg'] = df['Volume'].rolling(window=5).mean()
    
    # --- Get the latest data for our checks ---
    latest = df.iloc[-1] # The last row of the DataFrame
    previous = df.iloc[-2] # The second to last row

    # --- Run the Screener Logic ---
    # Condition 1: RSI is below 45
    rsi_ok = latest['RSI_14'] < 45

    # Condition 2: Last two candles are bullish (Close > Open)
    candles_ok = (latest['Close'] > latest['Open']) and (previous['Close'] > previous['Open'])

    # Condition 3: Volume Spike (latest volume is 1.5x the 5-day average)
    volume_ok = latest['Volume'] > (latest['Volume_5d_avg'] * 1.5)

    # Note: We will add the weekly volume check later to keep this simple for now.

    # --- Final Check ---
    # If all conditions are true, this stock is a match!
    if rsi_ok and candles_ok and volume_ok:
        print(f"✅ MATCH FOUND: {df.name}")
        return True
    else:
        # Optional: Print why it failed for debugging
        # print(f"❌ No match for {df.name}: RSI OK={rsi_ok}, Candles OK={candles_ok}, Volume OK={volume_ok}")
        return False

def run_screener():
    """Main function to run the screener on all specified stocks."""
    print("--- Starting Nepse Screener ---")
    buy_signals = []
    
    for symbol in STOCKS_TO_SCREEN:
        print(f"Analyzing {symbol}...")
        df = get_historical_data(symbol)
        if df is not None:
            df.name = symbol # Store symbol name for easy reference
            if analyze_stock(df):
                buy_signals.append(symbol)
                
    print("--- Screener Finished ---")
    return buy_signals

# This block allows us to run this file directly from the terminal for testing
if __name__ == "__main__":
    signals = run_screener()
    if signals:
        print(f"\n🔥 Stocks with potential buy signals: {signals}")
    else:
        print("\nNo stocks matched the criteria today.")
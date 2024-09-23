import yfinance as yf
import pandas as pd
import numpy as np

def fetch_stock_data(symbol, start_date=None, end_date=None):
    """
    Fetch stock data for a given symbol within a specified date range.
    
    Args:
    symbol (str): Stock symbol
    start_date (str): Start date for historical data (format: 'YYYY-MM-DD')
    end_date (str): End date for historical data (format: 'YYYY-MM-DD')
    
    Returns:
    tuple: (DataFrame with historical data, dict with stock info)
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(start=start_date, end=end_date)
        info = stock.info
        return df, info
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, None

def get_stock_info(info):
    """
    Extract relevant stock information from the info dictionary.
    
    Args:
    info (dict): Stock information dictionary
    
    Returns:
    pd.DataFrame: DataFrame with selected stock information
    """
    relevant_info = {
        'Sector': info.get('sector', 'N/A'),
        'Industry': info.get('industry', 'N/A'),
        '52 Week High': f"${info.get('fiftyTwoWeekHigh', 'N/A'):.2f}",
        '52 Week Low': f"${info.get('fiftyTwoWeekLow', 'N/A'):.2f}",
        'Volume': f"{info.get('volume', 'N/A'):,}",
        'Avg Volume': f"{info.get('averageVolume', 'N/A'):,}",
        'Dividend Yield': f"{info.get('dividendYield', 'N/A'):.2%}" if info.get('dividendYield') else 'N/A',
    }
    return pd.DataFrame(list(relevant_info.items()), columns=['Metric', 'Value'])

def calculate_moving_averages(df, windows=[50, 200]):
    """
    Calculate moving averages for given windows.
    
    Args:
    df (pd.DataFrame): DataFrame with stock price data
    windows (list): List of window sizes for moving averages
    
    Returns:
    pd.DataFrame: DataFrame with added moving average columns
    """
    for window in windows:
        df[f'MA{window}'] = df['Close'].rolling(window=window).mean()
    return df

def calculate_rsi(df, window=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
    df (pd.DataFrame): DataFrame with stock price data
    window (int): RSI window size
    
    Returns:
    pd.DataFrame: DataFrame with added RSI column
    """
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

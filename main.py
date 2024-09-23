import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils import fetch_stock_data, get_stock_info, calculate_moving_averages, calculate_rsi
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Data Visualizer", layout="wide")

st.title("Stock Data Visualization App")

# User input for multiple stock symbols
stock_symbols = st.text_input("Enter stock symbols separated by commas (e.g., AAPL, GOOGL):", "AAPL, MSFT").upper()
stock_list = [symbol.strip() for symbol in stock_symbols.split(',')]

# Date range selection
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", datetime.now() - timedelta(days=365))
with col2:
    end_date = st.date_input("End Date", datetime.now())

if stock_symbols and start_date < end_date:
    # Fetch stock data for all symbols
    stock_data = {}
    for symbol in stock_list:
        df, info = fetch_stock_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if df is not None and info is not None:
            df = calculate_moving_averages(df)
            df = calculate_rsi(df)
            stock_data[symbol] = {'df': df, 'info': info}

    if stock_data:
        # Display comparative key financial information
        st.header("Stock Comparison")
        cols = st.columns(len(stock_data))
        for i, (symbol, data) in enumerate(stock_data.items()):
            with cols[i]:
                st.subheader(f"{data['info']['longName']} ({symbol})")
                st.metric("Current Price", f"${data['info']['currentPrice']:.2f}")
                st.metric("Market Cap", f"${data['info']['marketCap']:,.0f}")
                st.metric("P/E Ratio", f"{data['info']['trailingPE']:.2f}" if 'trailingPE' in data['info'] else "N/A")

        # Display interactive chart for price comparison with technical indicators
        st.subheader("Stock Price History Comparison with Technical Indicators")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, row_heights=[0.7, 0.3])

        for symbol, data in stock_data.items():
            df = data['df']
            fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name=f"{symbol} Close"), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MA50'], mode='lines', name=f"{symbol} 50-day MA", line=dict(dash='dash')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['MA200'], mode='lines', name=f"{symbol} 200-day MA", line=dict(dash='dot')), row=1, col=1)
            fig.add_trace(go.Scatter(x=df.index, y=df['RSI'], mode='lines', name=f"{symbol} RSI"), row=2, col=1)

        fig.update_layout(
            height=800,
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            yaxis2_title="RSI",
        )
        fig.update_yaxes(title_text="RSI", range=[0, 100], row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

        # Display stock information tables
        st.subheader("Stock Information")
        for symbol, data in stock_data.items():
            with st.expander(f"{symbol} Information"):
                stock_info = get_stock_info(data['info'])
                st.table(stock_info)

        # CSV download buttons
        st.subheader("Download Data")
        for symbol, data in stock_data.items():
            csv = data['df'].to_csv(index=True)
            st.download_button(
                label=f"Download {symbol} CSV",
                data=csv,
                file_name=f"{symbol}_stock_data.csv",
                mime="text/csv",
            )
    else:
        st.error("Unable to fetch stock data. Please check the stock symbols and try again.")
else:
    if start_date >= end_date:
        st.error("Start date must be before end date.")
    else:
        st.info("Please enter stock symbols to view their data.")

# Add footer
st.markdown("---")
st.markdown("Data provided by Yahoo Finance")

import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objs as go
import yfinance as yf
import plotly.offline as pyo

# Title of the web app
st.title("Stock Analyzer")

# Symbol input
symbol = st.text_input("Enter Stock Symbol (e.g., IBM):")

# Date range input
end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=15)

# Download historical stock data using yfinance
stock_df = yf.download(symbol, start=start_date, end=end_date)

# Create a Plotly figure
fig = go.Figure()

# Check if data is available
if not stock_df.empty:
    # Add actual stock data trace
    fig.add_trace(go.Scatter(x=stock_df.index,
                  y=stock_df['Close'], mode='lines', name='Actual Stock', line=dict(color='green')))

    # Streamlit app
    if st.button("Analyze"):
        # Calculate the 13-day and 8-day simple moving averages
        stock_df['SMA_13'] = stock_df['Close'].rolling(window=13).mean()
        stock_df['SMA_8'] = stock_df['Close'].rolling(window=8).mean()

        # Create a list to hold crossover points
        crossover_signals = []

        # Initialize the previous signal
        previous_signal = None

        for date, sma_13, sma_8 in zip(stock_df.index, stock_df['SMA_13'], stock_df['SMA_8']):
            if sma_8 > sma_13:
                signal = 'Buy Signal'
            else:
                signal = 'Sell Signal'

            if signal != previous_signal:
                crossover_signals.append((date, signal, sma_8))
                previous_signal = signal

        # Extract buy and sell dates
        buy_dates = [point[0]
                     for point in crossover_signals if point[1] == 'Buy Signal']
        sell_dates = [point[0]
                      for point in crossover_signals if point[1] == 'Sell Signal']

        # Highlight Buy and Sell signals
        fig.add_trace(go.Scatter(x=buy_dates, y=[stock_df.loc[date, 'SMA_8'] for date in buy_dates],
                                 mode='markers', name='Buy Signal', marker=dict(color='green')))
        fig.add_trace(go.Scatter(x=sell_dates, y=[stock_df.loc[date, 'SMA_8'] for date in sell_dates],
                                 mode='markers', name='Sell Signal', marker=dict(color='red')))

        # Create annotations for crossover points
        crossover_annotations = []

        for point in crossover_signals:
            if point[1] == 'Buy Signal':
                color = 'green'
            else:
                color = 'red'

            annotation = dict(
                x=point[0],
                y=point[2],
                xref='x',
                yref='y',
                text=point[1],
                showarrow=True,
                arrowhead=5,
                ax=0,
                ay=-30,
                bgcolor=color,
            )
            crossover_annotations.append(annotation)

        # Update the layout with the annotations
        fig.update_layout(annotations=crossover_annotations)

        # Show the plot in the Streamlit app
        st.plotly_chart(fig)

# This part of the code is outside the "if not stock_df.empty" block.
# It will execute even if there's no stock data.
# You can choose to keep or modify this part based on your requirements.
pyo.plot(fig, filename='stock_plot.html')

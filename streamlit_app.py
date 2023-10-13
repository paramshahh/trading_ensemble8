
import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import plotly.graph_objs as go
import yfinance as yf
import plotly.offline as pyo

st.set_page_config(page_title="Financial Analysis", page_icon="💹", layout="wide")

st.title("Financial Analysis")
st.sidebar.subheader("Parameters")

symbol = st.sidebar.text_input("Enter Stock Symbol", "NVDA")
sma_interval_1 = st.sidebar.number_input("Enter the first Moving Average interval (e.g., 8)", 1, 100, 8)
sma_interval_2 = st.sidebar.number_input("Enter the second Moving Average interval (e.g., 13)", 1, 100, 13)

end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=60)
stock_df = yf.download(symbol, start=start_date, end=end_date)

st.write("## Stock Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Close'], mode='lines', name='Actual Stock', line=dict(color='green')))
st.plotly_chart(fig)

key = open('/Users/paramshah/Desktop/project_chatbot/alphakey.txt').read()

url_sma_1 = f'https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=weekly&time_period={sma_interval_1}&series_type=close&apikey={key}'
url_sma_2 = f'https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=weekly&time_period={sma_interval_2}&series_type=close&apikey={key}'

response_sma_1 = requests.get(url_sma_1)
response_sma_2 = requests.get(url_sma_2)

data_sma_1 = response_sma_1.json()
data_sma_2 = response_sma_2.json()

sma_data_1 = data_sma_1.get("Technical Analysis: SMA", {})
sma_data_2 = data_sma_2.get("Technical Analysis: SMA", {})

sma_df_1 = pd.DataFrame(sma_data_1).T
sma_df_2 = pd.DataFrame(sma_data_2).T

sma_df_1.index = pd.to_datetime(sma_df_1.index)
sma_df_2.index = pd.to_datetime(sma_df_2.index)

sma_df_1 = sma_df_1.sort_index()
sma_df_2 = sma_df_2.sort_index()

sma_df_1 = sma_df_1[(sma_df_1.index >= start_date) & (sma_df_1.index <= end_date)]
sma_df_2 = sma_df_2[(sma_df_2.index >= start_date) & (sma_df_2.index <= end_date)]

st.write(f"## Moving Averages ({sma_interval_1}-day SMA)")
st.write(sma_df_1)

st.write(f"## Moving Averages ({sma_interval_2}-day SMA)")
st.write(sma_df_2)

crossover_signals = []

previous_signal = None  
for date, row_1, row_2 in zip(sma_df_1.index, sma_df_1['SMA'], sma_df_2['SMA']):
    if row_2 > row_1:
        signal = 'Sell Signal'
    else:
        signal = 'Buy Signal'
    
    if signal != previous_signal:
        crossover_signals.append((date, signal, row_2))
        previous_signal = signal

buy_dates = [point[0] for point in crossover_signals if point[1] == 'Sell Signal']
sell_dates = [point[0] for point in crossover_signals if point[1] == 'Buy Signal']

st.write("## Buy/Sell Signals")
st.write("### Sell Signals")
st.write(buy_dates)

st.write("### Buy Signals")
st.write(sell_dates)

st.write("## Stock Chart with Buy/Sell Signals")
fig = go.Figure()
fig.add_trace(go.Scatter(x=sma_df_1.index, y=sma_df_1['SMA'], mode='lines', name=f'{sma_interval_1}-day SMA'))
fig.add_trace(go.Scatter(x=sma_df_2.index, y=sma_df_2['SMA'], mode='lines', name=f'{sma_interval_2}-day SMA'))
fig.add_trace(go.Scatter(x=stock_df.index, y=stock_df['Close'], mode='lines', name='Actual Stock', line=dict(color='green')))

fig.add_trace(go.Scatter(x=buy_dates, y=[sma_df_2.loc[date, 'SMA'] for date in buy_dates], 
                         mode='markers', name='Sell Signal', marker=dict(color='red')))
fig.add_trace(go.Scatter(x=sell_dates, y=[sma_df_2.loc[date, 'SMA'] for date in sell_dates], 
                         mode='markers', name='Buy Signal', marker=dict(color='green')))

st.plotly_chart(fig)

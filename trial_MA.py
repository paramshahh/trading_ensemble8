import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objs as go
import yfinance as yf
import plotly.offline as pyo

symbol = 'IBM'
end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=15)

key = open('/Users/paramshah/Desktop/project_chatbot/alphakey.txt').read()

stock_df = yf.download(symbol, start=start_date, end=end_date)

url_13 = f'https://www.alphavantage.co/query?function=SMA&symbol=IBM&interval=weekly&time_period=13&series_type=close&apikey={key}'
response_13 = requests.get(url_13)
data_13 = response_13.json()
sma_data_13 = data_13["Technical Analysis: SMA"]

sma_df_13 = pd.DataFrame(sma_data_13).T
sma_df_13.index = pd.to_datetime(sma_df_13.index)
sma_df_13 = sma_df_13.sort_index()

url_8 = f'https://www.alphavantage.co/query?function=SMA&symbol=IBM&interval=weekly&time_period=8&series_type=close&apikey={key}'
response_8 = requests.get(url_8)
data_8 = response_8.json()
sma_data_8 = data_8["Technical Analysis: SMA"]

sma_df_8 = pd.DataFrame(sma_data_8).T
sma_df_8.index = pd.to_datetime(sma_df_8.index)
sma_df_8 = sma_df_8.sort_index()

end_date = datetime.now()
start_date = end_date - pd.DateOffset(months=15)
sma_df_13 = sma_df_13[(sma_df_13.index >= start_date)
                      & (sma_df_13.index <= end_date)]
sma_df_8 = sma_df_8[(sma_df_8.index >= start_date)
                    & (sma_df_8.index <= end_date)]

fig = go.Figure()

fig.add_trace(go.Scatter(x=sma_df_13.index,
              y=sma_df_13['SMA'], mode='lines', name='13-day SMA'))
fig.add_trace(go.Scatter(x=sma_df_8.index,
              y=sma_df_8['SMA'], mode='lines', name='8-day SMA'))
fig.add_trace(go.Scatter(x=stock_df.index,
              y=stock_df['Close'], mode='lines', name='Actual Stock', line=dict(color='green')))


crossover_signals = []

previous_signal = None
for date, row_13, row_8 in zip(sma_df_13.index, sma_df_13['SMA'], sma_df_8['SMA']):
    if row_8 > row_13:
        signal = 'Buy Signal'
    else:
        signal = 'Sell Signal'

    if signal != previous_signal:
        crossover_signals.append((date, signal, row_8))
        previous_signal = signal

buy_dates = [point[0]
             for point in crossover_signals if point[1] == 'Buy Signal']
sell_dates = [point[0]
              for point in crossover_signals if point[1] == 'Sell Signal']

fig.add_trace(go.Scatter(x=buy_dates, y=[sma_df_8.loc[date, 'SMA'] for date in buy_dates],
                         mode='markers', name='Buy Signal', marker=dict(color='green')))
fig.add_trace(go.Scatter(x=sell_dates, y=[sma_df_8.loc[date, 'SMA'] for date in sell_dates],
                         mode='markers', name='Sell Signal', marker=dict(color='red')))

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

pyo.plot(fig, filename='stock_plot.html')

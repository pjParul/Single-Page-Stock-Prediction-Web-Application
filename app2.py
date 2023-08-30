import pandas as pd
from pandas.io.formats import style
from pandas_datareader import data as pdr
from datetime import datetime as date
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import plotly.express as px
import yfinance as yf
from dash.exceptions import PreventUpdate
from model import predict
from plotly.graph_objects import Layout
from plotly.validator_cache import ValidatorCache

app = dash.Dash()

def get_stock_price_fig(df):
    fig = px.line(df,x= "Date" ,y= ["Close", "Open"], title="Closing and Opening Price vs Date" ,markers=True)
    fig.update_layout(title_x=0.5)
    return fig

def get_more(df):
    df['EWA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    fig = px.scatter(df,x= "Date",y= "EWA 20" ,title="Exponential Moving Average vs Date")
    fig.update_traces(mode= "lines+markers")
    return fig


app.layout = html.Div([
        html.Div([
            html.Div([
           html.H1(children= "Welcome to the Stock Dash App!")
            ],
            className= 'start',
           style = {'padding-top' :'1%'}
            ),
            html.Div([
              # stock code input
             dcc.Input(id='input', type= 'text' ,style={'align':'center'}),
             html.Button('Submit' ,id= 'submit-name', n_clicks =0),
            ]),
            html.Div(
              # Date range picker input
              ['Select a date range: ',
                           dcc.DatePickerRange(
                               id='my-date-picker-range',
                                min_date_allowed=date(1995, 8, 5),
                                max_date_allowed=date.now(),
                                initial_visible_month=date.now(),
                                end_date=date.now().date(),
                                style = {'font-size': '18px', 'display': 'inline-block', 'align': 'center', "border-radius" : '2px', 'border' : '1px solid #ccc', 'color': '#333'}
                                ),
             html.Div(id='output-container-date-picker-range',children= 'You have selected a date')
              ]),
            html.Div([
              # Stock price button
              html.Button('Stock Price', id='submit-val', n_clicks= 0, style={'float': 'left', 'padding': '15px 32px', 'background-color': 'red', 'display': 'inline'}),
              html.Div(id="container-button-basic"),
              # Indicators button
              html.Button('Indicator', id='submit-ind', n_clicks= 0),

              # no of days of forecast input
              html.Div([dcc.input(id='Forcast_Input', type='text')]),
              html.Button('No of days to forecast',id='submit-force',n_clicks=0),
              html.Div(id='forecast')
              # forecast button
        ])
],className='nav'),

html.Div(
    [
        html.Div(
            [
                html.Img(id='logo'),
                html.H1(id='name')

                # company name
            ],
            className="header"),
        html.Div(# description
                 id='description',className='description_ticker'),
        html.Div([],
                 # stock price plot
                 id='graphs-content'),
        html.Div([
            # indicator plot
        ],id='main-content'),
        html.Div([
            # forecast plot
        ], id="Forecast-content")
    ],
    className='content')],
className = 'container')


@app.callback([
    Output('description','children'),
    Output('logo','src'),
    Output('name','children'),
    Output('submit-val','n_clicks'),
    Output('submit-ind','n_clicks'),
    Output('submit-forc','n_clicks'),
    Input('submit-name','n_clicks'),
    State('Input','value')
])

def update_data(n,val):
    if n==None:
        return "Hey there! Please enter a legitimate stock code to get details"
    # raise PreventUpdate
    else:
        if val==None:
            raise PreventUpdate
        else:
            ticker=yf.ticker(val)
            inf=ticker.info
            df = pd.DataFrame().from_dict(inf, orient='index').T
            df[['logo-url','shortName','longBusinessSummary']]
            return df['longBusinessSummary'].values[0],df['logo-url'].values[0],df['shortName'].values[0],None,None,None

@app.callback([
    Output('graphs-content','children'),
    Input('submit-val','n_clicks'),
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date'),
    State('Input','value')
])

def update_graph(n,start_date,end_date,val):
    if n==None:
        return [""]
    # raise PreventUpdate
    if val==None:
        raise PreventUpdate
    else:
        if start_date != None:
            df = yf.download(val,str(start_date),str(end_date))
        else:
            df = yf.download(val)
            df.reset_index(inplace=True)
            fig = get_stock_price_fig(df)
            return [dcc.Graph(figure=fig)]

@app.callback([Output("main-content",'children')],[
    Input('submit-ind','n_clicks'),
    Input('my-date-picker-range','start_date'),
    Input('my-date-picker-range','end_date'),
],
    [State('Input','value')
])

def indicators(n,start_date,end_date,val):
    if n==None:
        return ['']
    if val==None:
        return [""]

    if start_date == None:
        df_more = yf.download(val)
    else:
        df_more = yf.download(val, str(start_date), str(end_date))

    df_more.reset_index(inplace=True)
    fig = get_more(df_more)
    return [dcc.Graph(figure=fig)]

@app.callback([
    Output("forecast-content",'children'),
    Input('submit-forc','n_clicks'),
    State('Forcast_Input','value'),
    State('Input','value')
])

def forecast(n,n_days,val):
    if n==None:
        return [""]
    if val == None:
        raise PreventUpdate

    x = int(n_days)
    fig = predict(val,x+1)
    return [dcc.Graph(figure=fig)]

if __name__ == '__main__':
    app.run_server(debug=True)
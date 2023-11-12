# Package Import
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import Input, Output, dcc, html
from flask import Flask

# Reading in data
df = pd.read_csv('irs_audit_data.csv')
us_df = df[df.State != 'US']
options = list(us_df.columns[3:])

# Building Dashboard Application
server = Flask(__name__)
app = dash.Dash(server= server, external_stylesheets=[dbc.themes.CYBORG])
controls = dbc.Card(
    [html.Div(
        [
            dbc.Label("IRS Tax Filing Variables"),
            dcc.Dropdown(id="parameter", options=[{"label": col, "value": col} for col in options],
                         value="Number of returns", style={'color': 'Black', 'font-size': 17}),
        ], style={'color': 'Gold', 'font-size': 17}
    ),
        html.Div(
            [dbc.Label("Years"),
                dcc.Dropdown(
                    id="year",
                    options=[
                        {"label": col, "value": col} for col in us_df.Year.unique()
                    ],
                    value=2012, style={'color': 'Black', 'font-size': 17})
             ],
        style={'color': 'Gold', 'font-size': 20})

    ],
    body=True,
)
app.layout = html.Div([html.Div([dbc.Container(
    [
        html.H1("US Tax Filing Dashboard"),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=4),
                dbc.Col(dcc.Graph(id="geo_map"), md=8),
            ],
            align="left",
        ),
    ],
)]), html.Div([dbc.Container([html.Hr(style={'color': 'white', 'font-size': 20}), html.Div(
    [
        dbc.Label("US States"),
        dcc.Dropdown(
            id="state",
            options=[
                {"label": col, "value": col} for col in us_df.State.unique()
            ],
            value="CA", style={'color': 'Black', 'font-size': 20}
        )
    ], style={'color': 'Gold', 'font-size': 20}),
    html.Div(
    [
        dbc.Row(
            [
                # dbc.Col(html.Div(dcc.Graph(id='graph1'))),
                dbc.Col(html.Div(dcc.Graph(id="graph2"))),
                dbc.Col(html.Div(dcc.Graph(id="graph3"))),
                dbc.Col(html.Div(dcc.Graph(id="graph4")))
            ]
        ),

    ]
)
])
])
])


@app.callback(
    Output("geo_map", "figure"),
    [
        Input("parameter", "value"),
        Input("year", "value"),
    ],
)
def make_graph(parameter, year):
    df = us_df[us_df.Year == year][['State', parameter]]
    fig = go.Figure(data=go.Choropleth(
        locations=df['State'],  # Spatial coordinates
        z=df[parameter].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='fall',
        colorbar_title="Millions USD"
    ))
    if 'Amount' in parameter:

        fig.update_layout(
            title_text='{} in {} (in thousands of dollards)'.format(
                parameter, year),
            geo_scope='usa',  # limite map scope to USA
        )
    else:
        fig.update_layout(
            title_text='{} in {}'.format(parameter, year),
            geo_scope='usa',  # limite map scope to USA
        )

    fig.update_layout(
        autosize=False,
        margin=dict(l=0, r=200, b=0, t=35, pad=0, autoexpand=False),
        width=850,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        font=dict(color="white")
    )
    fig.add_scattergeo(
        locations=df['State'],
        locationmode="USA-states",
        text=df['State'],
        mode='text')

    return fig


@app.callback(
    # Output("graph1", "figure"),
    Output("graph2", "figure"),
    Output("graph3", "figure"),
    Output("graph4", "figure"),
    Input("state", "value"),

)
def make_graph(state):
    graph_list = []
    new_df1 = us_df[us_df.State == state]
    new_df2 = new_df1.copy()
    new_df2['Year'] = new_df2.Year.astype(str)
    df = new_df2[['Year',
                  'Number of dependents',
                  'Number of exemptions',
                  'Number of \r\nfarm returns',
                  'Child tax credit Number of returns',
                  'Number of joint returns']]

    fig2 = px.line(
        df,
        x='Year',
        y=df.columns[2],
        markers=True,
        title='Number of Exemptions',
        labels={
            'Year': '',
            'Number of exemptions': ''})
    fig2.update_layout(plot_bgcolor="#125771")
    fig2.update_traces(line=dict(color='#E4FA06', width=4))
    fig2.update_layout(margin=dict(l=0, r=5, b=0, t=35, pad=0))
    fig2.update_traces(marker=dict(size=12))
    graph_list.append(fig2)

    fig3 = px.line(
        df,
        x='Year',
        y=df.columns[3],
        markers=True,
        title='Number of farm returns',
        labels={
            'Year': '',
            'Number of \r\nfarm returns': ''})
    fig3.update_layout(plot_bgcolor="#125771")
    fig3.update_traces(line=dict(color='#FBFCFC', width=4))
    fig3.update_layout(margin=dict(l=0, r=5, b=0, t=35, pad=0))
    fig3.update_traces(marker=dict(size=12))
    graph_list.append(fig3)

    fig4 = px.line(
        df,
        x='Year',
        y=df.columns[4],
        markers=True,
        title='Child tax credit-Number of returns',
        labels={
            'Year': '',
            'Child tax credit Number of returns': ''})
    fig4.update_layout(plot_bgcolor="#125771")
    fig4.update_traces(line=dict(color='#06EFFA', width=4))
    fig4.update_traces(marker=dict(size=12))
    fig4.update_layout(margin=dict(l=0, r=5, b=0, t=35, pad=0))
    graph_list.append(fig4)
    return fig2, fig3, fig4


if __name__=='__main__':
    app.run_server(host = '0.0.0.0', port='5000')

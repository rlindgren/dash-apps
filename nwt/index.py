from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

from app import app
from apps import annual, monthly


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print( pathname )
    if pathname == '/apps/annual':
        return annual.layout
    elif pathname == '/apps/monthly':
        return monthly.layout
    elif pathname == '/':
        return pathname
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=True)
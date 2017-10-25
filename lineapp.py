import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# load the data
df = pd.read_csv( './data/tas_mean_NCAR-CCSM4_rcp85_annual_decadals_profiles_nwt_mine_sites.csv', index_col=0 )

def melt_it( df ):
    df = df.reset_index()
    cols = list(df.columns)
    cols[0] = 'year'
    df.columns = cols
    df = df.melt( id_vars=['year', 'rand'], value_vars=[i for i in df.columns if i is not 'year' and i is not 'rand'])
    cols = ['year','rand','minesite','tas']
    df.columns = cols
    df['year'] = [ int(i.split('s')[0]) for i in df.year ]
    df['rand'] = 0
    for val, mine_loc in enumerate(df.minesite.unique()):
        df.iloc[ np.where(df.minesite == mine_loc)[0], np.where(df.columns == 'rand')[0] ] = val
    return df

df = melt_it( df )

# map colors to mines for consistency when adding multiple lines. 
colors = { 'CanTung_Mine':'rgb(140,86,75)', 'Diavik_Mine':'rgb(41,119,179)', 'Ekati_Mine':'rgb(235,124,50)', 
            'Gahcho_Kue_Mine':'rgb(212,56,46)', 'NICO_Mine':'rgb(145,101,185)', 
            'Pine_Point_Mine_(Tamerlane)':'rgb(223,117,190)', 'Prairie_Creek_Mine':'rgb(125,125,125)',
            'Snap_Lake_Mine':'rgb(81,158,46)' }

app = dash.Dash()

markdown_head = ''' 
# Northwest Territories Mine Sites
### Decadal Mean Annual Temperature

'''

app.layout = html.Div([
    dcc.Markdown( children=markdown_head ),
    # html.H1( 'Northwest Territories Mine Sites'),
    # html.H2( 'Decadal Mean Annual Temperature' ),
    dcc.Dropdown(
        id='my-dropdown',
        options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
        value=['Snap_Lake_Mine','CanTung_Mine'],
        multi=True
    ),
    dcc.Graph( id='my-graph' ),
    dcc.RangeSlider( id='range-slider',
            marks={str(year): str(year) for year in df['year'].unique()},
            min=df['year'].min(),
            max=df['year'].max(),
            step=1,
            value=[df['year'].unique().min(), df['year'].unique().max()]
    )
])

@app.callback( Output('my-graph', 'figure'), 
                [Input('my-dropdown', 'value'),
                Input('range-slider', 'value')] )
def update_graph(selected_dropdown_value, year_range):
    # print(year_range) # for testing
    filtered_df = df[ df.minesite.isin( selected_dropdown_value ) ]
    begin_range, end_range = year_range
    filtered_df = filtered_df[ (filtered_df['year'] >= begin_range) & (filtered_df['year'] <= end_range) ]

    return {'data':[ go.Scatter( x=filtered_df.loc[filtered_df.minesite == v, 'year'], 
                        y=filtered_df.loc[filtered_df['minesite'] == v, 'tas'], 
                        name=v.replace('_', ' '), 
                        line=dict(color=colors[v], width=2 )) 
                            for v in selected_dropdown_value ] }

if __name__ == '__main__':
    app.run_server( debug=True )
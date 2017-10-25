import dash, os, glob
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# load the data constants
# df = pd.read_csv( './tas_mean_NCAR-CCSM4_rcp85_annual_decadals_profiles_nwt_mine_sites.csv', index_col=0 )
pts = pd.read_csv( './minesites.csv', index_col=0 )
mapbox_access_token = 'pk.eyJ1IjoiZWFydGhzY2llbnRpc3QiLCJhIjoiY2o4b3J5eXdwMDZ5eDM4cXU4dzJsMGIyZiJ9.a5IlzVUBGzJbQ0ayHC6t1w'
group = 'annual_decadals'
scenarios = ['rcp45', 'rcp85']
# models = ['5ModelAvg', 'GFDL-CM3', 'GISS-E2-R', 'IPSL-CM5A-LR', 'MRI-CGCM3','NCAR-CCSM4']

def split_fn( fn ):
    dirname, basename = os.path.split( fn )
    d = dict(zip(['var','metric','model','scenario','timestep','agg'], 
                basename.split( '_' )[:6]))
    d.update( fn=fn ) # slice off junk at end
    return d

def melt_it( fn ):
    attrs = split_fn( fn )
    df = pd.read_csv( fn, index_col=0 )
    df = df.reset_index()
    cols = list( df.columns )
    cols[0] = 'year'
    df.columns = cols
    df = df.melt( id_vars=['year', 'rand'], value_vars=[i for i in df.columns if i is not 'year' and i is not 'rand'])
    cols = ['year','rand','minesite','tas']
    df.columns = cols
    df['year'] = [ int(i.split('s')[0]) for i in df.year ]
    df['rand'] = 0
    df['group'] = '{}_{}'.format(attrs['timestep'],attrs['agg'])
    df['model'] = attrs['model']
    df['scenario'] = attrs['scenario']
    for val, mine_loc in enumerate(df.minesite.unique()):
        df.iloc[ np.where(df.minesite == mine_loc)[0], np.where(df.columns == 'rand')[0] ] = val
    return df

df = pd.concat([ melt_it( fn ) for fn in glob.glob(os.path.join('.','data',group,'*.csv') )])



# map_config = dict(  id='my-map',
#                     type='scattermapbox',
#                     lon=pts['Longitude'],
#                     lat=pts['Latitude'],
#                     text=pts['Name'],
#                     name='test_MAP',
#                     marker=dict(
#                         size=4,
#                         opacity=0.6,
#                         color='rgb(140,86,75)' ) )

# traces = [go.Scattermapbox( id='my-map',
#                     type='scattermapbox',
#                     lon=pts['Longitude'],
#                     lat=pts['Latitude'],
#                     text=pts['Name'],
#                     name='test_MAP',
#                     marker=dict(
#                         size=4,
#                         opacity=0.6,
#                         color='rgb(140,86,75)' ) )]

map_data = [ go.Scattermapbox(
        lat=pts['Latitude'].tolist(),
        lon=pts['Longitude'].tolist(),
        mode='markers',
        marker=go.Marker(size=12, color='rgb(140,86,75)'),
        text=pts['Name'].tolist() )]

mapbox_config = dict(accesstoken=mapbox_access_token,
                        bearing=0,
                        pitch=10,
                        zoom=4,
                        center=dict(lat=pts['Latitude'].mean(),
                                    lon=pts['Longitude'].mean()))

map_layout = go.Layout(
    autosize=True,
    hovermode='closest',
    mapbox=mapbox_config )

map_figure = go.Figure( dict(data=map_data, layout=map_layout) )

# map_layout = dict(
#     autosize=True,
#     height=500,
#     font=dict(color='#CCCCCC'),
#     titlefont=dict(color='#CCCCCC', size='14'),
#     margin=dict(
#         l=35,
#         r=35,
#         b=35,
#         t=45
#     ),
#     hovermode="closest",
#     plot_bgcolor="#191A1A",
#     paper_bgcolor="#020202",
#     legend=dict(font=dict(size=10), orientation='h'),
#     title='Satellite Overview',
#     mapbox=dict(
#         accesstoken=mapbox_access_token,
#         style="dark",
#         center=dict(
#             lon=-78.05,
#             lat=42.54
#         ),
#         zoom=7,
#     )
# )

# map_figure = dict(data=traces, layout=map_layout)

# map colors to mines for consistency when adding multiple lines. 
colors = { 'CanTung_Mine':'rgb(140,86,75)', 'Diavik_Mine':'rgb(41,119,179)', 'Ekati_Mine':'rgb(235,124,50)', 
            'Gahcho_Kue_Mine':'rgb(223,117,190)', 'NICO_Mine':'rgb(81,158,46)', 
            'Pine_Point_Mine_(Tamerlane)':'rgb(212,56,46)', 'Prairie_Creek_Mine':'rgb(125,125,125)',
            'Snap_Lake_Mine':'rgb(145,101,185)' }

app = dash.Dash()

markdown_head = ''' 
# Northwest Territories Mine Sites
### Decadal Mean Annual Temperature

'''

app.layout = html.Div([
    dcc.Markdown( children=markdown_head ),
    dcc.Graph( id='my-map', figure=map_figure ),
    html.Label('Choose Scenario(s)'),
    dcc.Checklist( id='scenario-check',
        options=[{'label': i, 'value': i} for i in scenarios ], #df.scenario.unique()
        values=['rcp85']
    ),
    html.Label('Choose Model(s)'),
    dcc.Checklist( id='model-check',
        options=[{'label': i, 'value': i} for i in df.model.unique() ],
        values=['IPSL-CM5A-LR']
    ),    
    dcc.Dropdown(
        id='my-dropdown',
        options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
        value=['Ekati_Mine','Pine_Point_Mine_(Tamerlane)', 'NICO_Mine', 'Prairie_Creek_Mine'],
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
                Input('range-slider', 'value'),
                Input('scenario-check', 'values'),
                Input('model-check', 'values')] )
def update_graph(selected_dropdown_value, year_range, scenarios, models ):
    import itertools
    filtered_df = df[ df.minesite.isin( selected_dropdown_value ) ] 
    begin_range, end_range = year_range
    filtered_df = filtered_df[ (filtered_df['year'] >= begin_range) & (filtered_df['year'] <= end_range) ]

    # handle scenarios /  models ...
    args = itertools.product( scenarios, models, selected_dropdown_value )
    
    return {'data':[ go.Scatter( x=filtered_df.loc[ (filtered_df.scenario == s)&(filtered_df.model == m)&(filtered_df.minesite == v), 'year'], 
                        y=filtered_df.loc[ (filtered_df.scenario == s)&(filtered_df.model == m)&(filtered_df.minesite == v), 'tas'], 
                        name=v.replace('_', ' '), 
                        line=dict(color=colors[v], width=2 )) 
                            for s,m,v in args ] }


if __name__ == '__main__':
    app.run_server( debug=True )

# # # JUNK
# print(hoverdata) # for testing
# Input('my-map', 'hoverData')

# hoverdata = {'points': [{'lon': -128.268, 'pointNumber': 0, 'curveNumber': 0, 'text': 'CanTung Mine', 'lat': 61.972}]}
# new_selection = [ selected['text'].replace(' ', '_') for selected in hoverdata['points'] ]

import dash, os, glob, json
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import geopandas as gpd
import numpy as np

files = [ 'tas_minesites_decadal_annual_mean_alldata_melted.csv',
         'tas_minesites_decadal_monthly_mean_alldata_melted.csv' ]

files = [ os.path.join( '.','data',fn ) for fn in files ]
data = { count+1:pd.read_csv(fn, index_col=0) for count, fn in enumerate( files ) }

df = data[1] # use this to build out some stuff in the layout...

pts = pd.read_csv( './data/minesites.csv', index_col=0 )
nwt_shape = './data/NorthwestTerritories_4326.geojson'
mapbox_access_token = 'pk.eyJ1IjoiZWFydGhzY2llbnRpc3QiLCJhIjoiY2o4b3J5eXdwMDZ5eDM4cXU4dzJsMGIyZiJ9.a5IlzVUBGzJbQ0ayHC6t1w'
group = 'annual_decadals'
scenarios = ['rcp45', 'rcp60','rcp85']

# # # # CONFIGURE MAPBOX AND DATA OVERLAYS
ptsd = list(pts.T.to_dict().values())
# MINE_ORDER_REFERENCE = ['CanTung Mine', 'Diavik Mine', 'Ekati Mine', 'Gahcho Kue Mine', 'NICO Mine', 'Pine Point Mine (Tamerlane)', 'Prairie Creek Mine', 'Snap Lake Mine'] 
textpositions = ['top center','bottom center','top center','bottom right','middle left','top right','below center','bottom left']
map_traces = [ go.Scattermapbox(
            lat=[pt['Latitude']],
            lon=[pt['Longitude']],
            mode='markers+text',
            marker=go.Marker(size=12, color='rgb(140,86,75)'),
            text=[pt['Name']],
            textposition=tp ) for tp,pt in zip(textpositions, ptsd) ]


mapbox_config = dict(accesstoken=mapbox_access_token,
                        bearing=0,
                        pitch=0,
                        zoom=2,
                        center=dict(lat=65,
                                    lon=-118),
                        layers=[ dict( sourcetype='geojson',
                                        source=json.loads(open(nwt_shape,'r').read()),
                                        type='fill',
                                        color='rgba(163,22,19,0.1)',
                                        below=0 )]
                        )

map_layout = go.Layout(
                    autosize=True,
                    hovermode='closest',
                    mapbox=mapbox_config,
                    showlegend=False )

map_figure = go.Figure( dict(data=map_traces, layout=map_layout) )

ms_colors = {'GISS-E2-R':{'rcp45':'#FDD017','rcp60':'#F2BB66','rcp85':'#EAC117'},
            'GFDL-CM3':{'rcp45':'#6AA121','rcp60':'#347C17','rcp85':'#254117'},
            '5ModelAvg':{'rcp45':'#736F6E','rcp60':'#463E3F','rcp85':'#2B1B17'},
            'IPSL-CM5A-LR':{'rcp45':'#C24641','rcp60':'#7E3517','rcp85':'#800517'},
            'MRI-CGCM3':{'rcp45':'#4863A0','rcp60':'#2B547E','rcp85':'#151B54'},
            'NCAR-CCSM4':{'rcp45':'#C35817','rcp60':'#6F4E37','rcp85':'#493D26'} }


markdown_map = '''
#### How to use this application:
- Click minesite points in the map above 
to select a different mine to display
in the plot to the left.
- select single or multiple emissions scenarios 
which will update the line graph with the desired 
traces.
- select single or multiple models from the dropdown
menu to display different models.
- Use the range slider below the line graph to select 
the range of decades to be viewed.
- the line graphic is interactive and a toolbar will display
in the upper-right corner of the graphic upon hover, which 
provides some tools that can be used to customize the users view.

__NOTE: Putting too many combinations of models and scenarios
will generate a very busy graphic and there is a larger chance
for similar colors being used for different model-scenario groups.__


'''

app = dash.Dash()

markdown_head = ''' 
### Northwest Territories Mine Sites -- Decadal Mean Annual Temperature
'''

# app.layout = html.Div([ 
#                 html.Div([
#                     dcc.Markdown( children=markdown_head ),
#                     dcc.Tabs( 
#                         id='tabs',
#                         tabs=[ {'label': 'Annual Decadal Temps - minesites', 'value': 1},
#                                 {'label': 'Monthly Decadal Temps - minesites', 'value': 2} ],
#                         value=1,
#                         vertical=False
#                     ),
#                     html.Div([
#                         html.Div([ html.Label('Choose Minesite', style={'font-weight':'bold'}),
#                                  dcc.Dropdown( id='my-radio',
#                                     options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
#                                     value='Prairie_Creek_Mine',
#                                     multi=False,
#                                     )], className='three columns' ),

#                         html.Div([ html.Label('Choose Scenario(s)', style={'font-weight':'bold'}),
#                                 dcc.Checklist( id='scenario-check',
#                                     options=[{'label': i, 'value': i} for i in scenarios ], #df.scenario.unique()
#                                     values=['rcp85'],
#                                     labelStyle={'display': 'inline-block'}
#                                 )], className='three columns'),
#                         html.Div( id='month-div', className='two columns')
#                         ], className='row'),

#                 html.Div([ html.Label('Choose Model(s)', style={'font-weight':'bold'}),
#                     dcc.Dropdown(
#                         id='model-dropdown',
#                         options=[ {'label':i, 'value':i} for i in df.model.unique() ],
#                         value=['IPSL-CM5A-LR'],
#                         multi=True
#                         )
#                     ], className='eight columns'),

#                     dcc.Graph( id='my-graph' ),
#                     dcc.RangeSlider( id='range-slider',
#                         marks={str(year): str(year) for year in df['year'].unique()[::2]},
#                         min=df['year'].min(),
#                         max=df['year'].max(),
#                         step=2,
#                         value=[df['year'].unique().min(), df['year'].unique().max()]
#                     )], className="eight columns" ),
#                 html.Div([
#                     dcc.Graph( id='my-map', figure=map_figure ),
#                     dcc.Markdown( children=markdown_map )
#                     ], className="four columns" ),
#                 html.Div(id='intermediate-value'), #, style={'display': 'none'}
#                 ])



# Build App Layout
app.layout = html.Div([ 
                html.Div([
                    dcc.Markdown( children=markdown_head ),
                    dcc.Tabs( 
                        id='tabs',
                        tabs=[
                            {'label': 'Annual Decadal Temps - minesites', 'value': 1},
                            {'label': 'Monthly Decadal Temps - minesites', 'value': 2},
                            # {'label': 'Annual Decadal Temps - NWT', 'value': 3},
                            # {'label': 'Monthly Decadal Temps - NWT', 'value': 4},
                        ],
                        value=1,
                        vertical=False
                    ),
                ]),

                html.Div([ 
                    html.Div([
                        # dcc.RadioItems(    
                        #     id='my-radio',
                        #     options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
                        #     value='Prairie_Creek_Mine',
                        #     labelStyle={'display': 'inline-block'},
                        #     style={'width':'70%'}
                        # ),
                    html.Div([
                        html.Div([ html.Label('Choose Minesite', style={'font-weight':'bold'}),
                                 dcc.Dropdown( id='my-radio',
                                    options=[ {'label':i.replace('_', ' '), 'value':i} for i in df.minesite.unique() ],
                                    value='Prairie_Creek_Mine',
                                    multi=False,
                                    )], className='three columns' ),

                        html.Div([ html.Label('Choose Scenario(s)', style={'font-weight':'bold'}),
                                dcc.Checklist( id='scenario-check',
                                    options=[{'label': i, 'value': i} for i in scenarios ], #df.scenario.unique()
                                    values=['rcp85'],
                                    labelStyle={'display': 'inline-block'}
                                )], className='three columns'),
                        html.Div( id='month-div', className='two columns')
                        ], className='row'),


                        # html.Div([
                        #     html.Div([
                        #         html.Label('Choose Scenario(s)', style={'font-weight':'bold'}),
                        #         dcc.Checklist( id='scenario-check',
                        #             options=[{'label': i, 'value': i} for i in scenarios ], #df.scenario.unique()
                        #             values=['rcp85'],
                        #             labelStyle={'display': 'inline-block'}
                        #         )], className='six columns'),
                        #     html.Div([], id='month-div', className='six columns'),
                        # ], className='row'),
                        html.Label('Choose Model(s)', style={'font-weight':'bold'}),
                        dcc.Dropdown(
                            id='model-dropdown',
                            options=[ {'label':i, 'value':i} for i in df.model.unique() ],
                            value=['IPSL-CM5A-LR'],
                            multi=True
                        ),
                        dcc.Graph( id='my-graph' ),
                        dcc.RangeSlider( id='range-slider',
                            marks={str(year): str(year) for year in df['year'].unique()[::2]},
                            min=df['year'].min(),
                            max=df['year'].max(),
                            step=2,
                            value=[df['year'].unique().min(), df['year'].unique().max()]
                        )], className="eight columns" ),
                    html.Div([
                        dcc.Graph( id='my-map', figure=map_figure ),
                        dcc.Markdown( children=markdown_map )
                    ], className="four columns" ),
            ], className="row"),
        html.Div(id='intermediate-value'), #, style={'display': 'none'}
        ])


# THE DEFAULT PLOTLY DASH CSS FROM @chriddyp  
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})
app.config['suppress_callback_exceptions']=True

@app.callback( Output('my-graph', 'figure'), [Input('intermediate-value', 'children')] )
def update_graph( data ):
    print('updating graph')
    dff = pd.read_json( data ).sort_index()
    if '-' in str(dff.loc[0, 'x_axis']):
        # its monthlies -- above is a complete dirty hack
        return {'data':[ go.Scatter( x=j['year'], 
                    y=j['tas'], 
                    name=i[0]+' '+i[1], 
                    line=dict(color=ms_colors[i[0]][i[1]], width=2 ),
                    mode='lines') for i,j in dff.groupby(['model','scenario','month']) ] }
    else: 
        # its annuals
        return {'data':[ go.Scatter( x=j['year'], 
                                    y=j['tas'],
                                    name=i[0]+' '+i[1], 
                                    line=dict(color=ms_colors[i[0]][i[1]], width=2 ),
                                    mode='lines') for i,j in dff.groupby(['model','scenario']) ] }

@app.callback( Output('intermediate-value', 'children'), 
                [Input('tabs', 'value'),
                Input('my-radio', 'value'),
                Input('range-slider', 'value'),
                Input('scenario-check', 'values'),
                Input('model-dropdown', 'value'),
                Input('month-dropdown','value')
                ] )
def prep_data( selected_tab_value, minesite, year_range, scenario_values, model_values, month ):
    import itertools

    print( 'prepping data' ) # [ TEST ]

    df_select = data[ selected_tab_value ].copy()
    filtered_df = df_select[ df_select.minesite == minesite ]
    begin_range, end_range = year_range
    filtered_df = filtered_df[ (filtered_df['year'] >= begin_range) & (filtered_df['year'] <= end_range) ]
    filtered_df = filtered_df.loc[ filtered_df[ 'scenario' ].isin( scenario_values ), ]
    filtered_df = filtered_df.loc[ filtered_df[ 'model' ].isin( model_values ), ]

    if selected_tab_value == 2:
        print('month={}'.format(month))
        filtered_df = filtered_df[ filtered_df['month'] == month ]
        filtered_df['x_axis'] = [ '{}-{}'.format(*i) for i in zip(filtered_df.month.tolist(), filtered_df.year.tolist()) ]
    else:
        filtered_df['x_axis'] = filtered_df['year']

    filtered_df = filtered_df.reset_index(drop=True)

    return filtered_df.to_json()


@app.callback( Output('month-div', 'children'), [Input('tabs', 'value')] )
def show_hide_month_drop( selected_tab_value ):
    print('selected_tab_value = {}'.format(selected_tab_value))
    if selected_tab_value == 2:
        return [html.Label('Choose Month(s)', style={'font-weight':'bold'}),
                dcc.Dropdown(
                    id='month-dropdown',
                    options=[ {'label':i, 'value':i} for i in range(1, 12+1) ],
                    value=1,
                    multi=False,
                    disabled=False
                )]
    else:
        return '''

        '''

@app.callback( Output('my-radio', 'value'), [Input('my-map', 'clickData')])
def update_minesite_radio( clickdata ):
    if clickdata is not None: # make it draw the inital graph before a clickevent
        return clickdata['points'][0]['text'].replace(' ', '_')
    else:
        return 'Prairie_Creek_Mine'



if __name__ == '__main__':
    app.run_server( debug=True )

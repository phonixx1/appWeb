import base64
import io

from amundiScript import nan, pd, genDrawUpDrawDown
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go



def données(data):
    if pd.to_datetime(data['date'],format = '%d/%m/%Y', errors='coerce').notnull().all():
        data['date'] = pd.to_datetime(data['date'],format = '%d/%m/%Y')
    elif pd.to_datetime(data['date'],format = '%m/%d/%Y', errors='coerce').notnull().all():
        data['date'] = pd.to_datetime(data['date'],format = '%m/%d/%Y')
    
    data["returns"] = data["price"].pct_change().fillna(0)
    positiveCumReturn, negativeCumReturn = genDrawUpDrawDown(data["returns"],TRIGER)
    taglist = ['positiveCumReturn' if x is not nan else 'negativeCumReturn' for x in positiveCumReturn]
    sumCumReturns = [x if x is not nan else y for (x,y) in zip(positiveCumReturn, negativeCumReturn)]
    data['positiveCumReturn'] = pd.DataFrame(positiveCumReturn)
    data['negativeCumReturn'] = pd.DataFrame(negativeCumReturn)
    data['sumCumReturns'] = pd.DataFrame(sumCumReturns)
    data['taglist'] = pd.DataFrame(taglist)
    return data


TRIGER = 0.2
FILE_PATH = 'NFLX.csv'
DATA = données(pd.read_csv(FILE_PATH,sep=','))


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
app.title = "Returns analysis"

app.layout = html.Div([
    html.H1(children="Draw-up/Draw-down Analytics", style={"fontSize": "48px", 
        "color": "blue",'text-align':'center'},className="header-title"),
    html.P(
        children="Analyze of the draw-up and draw-down of cumulative returns"
        " of a time series ",
        style={'text-align':'center'},
        className="header-description",
    ),

    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
   
    html.P(
        children=" Example with Netflix data price. Try with our own data : must be *.csv file with at least 2 columns : 'date' and 'price' and sep is ' , ' ",),
    dcc.Graph(id="output-data-upload",
    ),
    
    html.Div( children = [
    html.P(
        children=" Interactive graphics and triggers! Choose your trigger and select your graph :",),
    dcc.Slider(
    id='my-slider',
    min=0.1,
    max=1,
    step=0.1,
    value=0.2),
    
   
    html.Div(id='slider-output-container'),
    html.Br(),
    dcc.Dropdown(id="type-filter", placeholder = 'Select your graph'),
    dcc.Graph(id="draw-chart",config={"displayModeBar": False}),
    dcc.Graph(id="draw-doble-bot-fill"),
    
    dcc.Graph(id="draw-doble-fill"), 
    ],
    className = "wrapper"),   
    
])


def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    return df

@app.callback([Output('output-data-upload', 'figure'),Output('type-filter', 'options'),Output('draw-doble-bot-fill', 'figure'),Output('draw-doble-fill', 'figure'),
                ],
              [Input('upload-data', 'contents'),
              Input('upload-data', 'filename'),Input('my-slider', 'value')])
def update_output(contents, name,value):
    global DATA 
    global TRIGER
    ctx = dash.callback_context
    if ctx.inputs['my-slider.value'] is not None:
        TRIGER = value
        DATA = données(DATA)

    if contents is not None:
        children = parse_contents(contents, name) 
        data = données(children)
        DATA = data
        
    fig1={
            "data": [
                {
                    "x": DATA["date"],
                    "y": DATA["price"],
                    "type": "lines",
                },
                
            ],
            "layout": {"title": "Overview of the price variation"},
        }
    fig2={
            "data": [
                {
                    "x": DATA["date"],
                    "y": DATA["negativeCumReturn"],
                    "type": "lines",
                    'name': 'draw-down',
                },
                {
                    "x": DATA["date"],
                    "y": DATA["positiveCumReturn"],
                    "type": "lines",
                    'name': 'draw-up',
                },
            ],
            "layout": {"title": "Display of draw-down/draw-up of cumulatif returns"},
        }
    fig3=px.area(DATA,x="date", y="sumCumReturns",color = 'taglist', line_group="taglist",)
    
    options = [{"label": draw_type, "value": draw_type}
            for draw_type in DATA.taglist.unique()]
    return fig1, options, fig2, fig3
    

@app.callback(
    Output('draw-chart', 'figure'),
    [
        Input("type-filter", "value"),
        Input('upload-data', 'contents'),
        Input('upload-data', 'filename'),
        Input('my-slider', 'value')
        
    ],
)
def update_charts(draw_type,contents, name,value):
    ctx = dash.callback_context
    global DATA
    global TRIGER
    if ctx.inputs['my-slider.value'] is not None:
        TRIGER = value
        DATA = données(DATA)
    
    if ctx.inputs['upload-data.contents'] is not None:
        children = parse_contents(contents, name) 
        data = données(children)
        DATA = data
        if ctx.inputs['type-filter.value'] is not None:
            mask = ((DATA.taglist == draw_type))
            filtered_data = DATA.loc[mask, :]
            drawup_figure = px.area(filtered_data,x=filtered_data['date'], y=filtered_data[draw_type])
        else:
            drawup_figure = {}

    elif ctx.inputs['type-filter.value'] is not None:
        mask = ((DATA.taglist == draw_type))
        filtered_data = DATA.loc[mask, :]
        drawup_figure = px.area(filtered_data,x=filtered_data['date'], y=filtered_data[draw_type])
    else :
        drawup_figure = {}

    return drawup_figure

@app.callback(
    Output('slider-output-container', 'children'),
    [Input('my-slider', 'value')])
def updateTrigger(value):
    return 'Triger = {} equivalent to a draw of {}% '.format(value,100*value)

if __name__ == '__main__':
    app.run_server(debug=True)
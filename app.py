import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from amundiScript import nan, pd, genDrawUpDrawDown

TRIGER = 0.2

# Put the path of your data
FILE_PATH = "/mnt/c/Users/Sacha/Documents/Python/dashApp/SPX.csv" 
data = pd.read_csv(FILE_PATH, sep=',')
data['date'] = pd.to_datetime(data['date'],format = '%d/%m/%Y')
data["returns"] = data["price"].pct_change().fillna(0)
positiveCumReturn, negativeCumReturn = genDrawUpDrawDown(data["returns"],TRIGER)
taglist = ['positiveCumReturn' if x is not nan else 'negativeCumReturn' for x in positiveCumReturn]
sumCumReturns = [x if x is not nan else y for (x,y) in zip(positiveCumReturn, negativeCumReturn)]

data['positiveCumReturn'] = pd.DataFrame(positiveCumReturn)
data['negativeCumReturn'] = pd.DataFrame(negativeCumReturn)
data['sumCumReturns'] = pd.DataFrame(sumCumReturns)
data['taglist'] = pd.DataFrame(taglist)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Draw-up/Draw-down Analytics", style={"fontSize": "48px", "color": "red",'text-align':'center'},),
        html.P(
            children="Analyze of the draw-up and draw-down of cumulative returns"
            " of a time series "
            ,
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["date"],
                        "y": data["price"],
                        "type": "lines",
                    },
                    
                ],
                "layout": {"title": "Overview of the price variation"},
            },
        ),
        dcc.Graph(
            figure=px.area(data,
            x="date", y="positiveCumReturn",title="Display of draw-up of cumulatif returns"
            )
            
        ),
        dcc.Graph(
            figure=px.area(data,
            x="date", y="negativeCumReturn",
            title="Display of draw-down of cumulatif returns"
            )
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["date"],
                        "y": data["negativeCumReturn"],
                        "type": "lines",
                        'name': 'draw-down',
                    },
                    {
                        "x": data["date"],
                        "y": data["positiveCumReturn"],
                        "type": "lines",
                        'name': 'draw-up',
                    },
                ],
                "layout": {"title": "Display of draw-down/draw-up of cumulatif returns"},
            },
        ),
        
        dcc.Graph(
        figure=px.area(data,
            x="date", y="sumCumReturns",color = 'taglist', 
            line_group="taglist",

                )
            
        ),

        
    ]
)

if __name__ == "__main__":
    app.run_server(debug=True)


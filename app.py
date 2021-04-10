import dash
import dash_core_components as dcc
import dash_html_components as html
from amundiScript import nan, pd, genDrawUpDrawDown

TRIGER = 0.2

# Put the path of your data
FILE_PATH = "/mnt/c/Users/Sacha/Documents/Python/dashApp/SPX.csv" 
data = pd.read_csv(FILE_PATH, sep=',')
data['date'] = pd.to_datetime(data['date'],format = '%d/%m/%Y')
data["returns"] = data["price"].pct_change().fillna(0)
positiveCumReturn, negativeCumReturn = genDrawUpDrawDown(data["returns"],TRIGER)
data['positiveCumReturn'] = pd.DataFrame(positiveCumReturn)
data['negativeCumReturn'] = pd.DataFrame(negativeCumReturn)

app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1(children="Draw-up/Draw-down Analytics",),
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
            figure={
                "data": [
                    {
                        "x": data["date"],
                        "y": data["positiveCumReturn"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "positiveCumReturn"},
            },
        ),
        dcc.Graph(
            figure={
                "data": [
                    {
                        "x": data["date"],
                        "y": data["negativeCumReturn"],
                        "type": "lines",
                    },
                ],
                "layout": {"title": "negativeCumReturn"},
            },
        ),
    ]
)


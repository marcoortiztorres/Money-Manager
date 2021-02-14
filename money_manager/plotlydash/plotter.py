import json
import plotly
import plotly.graph_objs as go

from money_manager.google_drive.objects import *


def create_plot(transactions_json, category):
    transactions_df = pd.DataFrame(transactions_json)
    categorised_df = transactions_df[transactions_df[CATEGORY_KEY] == category]

    figure = get_pie_graph_figure(categorised_df[SUB_CATEGORY_KEY].to_list(), categorised_df[COST_KEY].to_list())

    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def create_average_description_pie(transactions_json, category):
    mean_key = 'mean'
    transactions_df = pd.DataFrame(transactions_json)
    categorised_df = transactions_df[transactions_df[CATEGORY_KEY] == category]
    categorised_df_summary = categorised_df.groupby(SUB_CATEGORY_KEY).describe()[COST_KEY]

    figure = get_pie_graph_figure(categorised_df_summary.index.values.tolist(),
                                  categorised_df_summary[mean_key].to_list())

    graphJSON = json.dumps(figure, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def get_pie_graph_figure(labels_list, values_list):
    # colors = ['#7245c4', '#8d72cf', '#9a9bd4', '#84b2d6', '#59cace', '#1ccfba', '#1ccfba',
    #           '#8661cb', '#9e83d4', '#9196ce', '#86b2cf', '#65cfcb', '#34d7bc', '#08d4b3',
    #           '#9f79d0', '#9f79d0', '#b5aad2', '#b5aad2', '#b5aad2', '#61d5c2', '#36d6bc']
    # figure.update_traces(hoverinfo='percent', textinfo='label+value', textfont_size=11, marker = dict(colors=colors))

    figure = go.Figure(
        data=[
            go.Pie(labels=labels_list,
                   values=values_list,
                   showlegend=False
                   )
        ]
    )
    figure.update_traces(hoverinfo='percent', textinfo='label+value', textfont_size=11)
    return figure

import numpy as np
from dash import html, dcc, Input, Output, Dash
import plotly.graph_objects as go
import plotly
import plotly.express as px
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc

load_figure_template(["darkly"])


def dash_plot_images(x=None, y=None, xlim=None, ylim=None, color_code=None,
                     cmap_plot='Viridis', marker_size=10,
                     images=None, cmap_images='inferno',
                     image_labels=None):
    '''
    Plotting function that uses Dash to plot galaxies in a 2d plane of properties and shows their spectra by hovering over the points.
    
    Input
    -----
    x,y : Python dictionaries
          The coordinates of the data points to be plotted.
          Can be anything measured for every galaxy, e.g. x=Mass, y=SFR.
          Dictionary labels are the axis titles.

    xlim: list or tuple (xmin,xmax)
          set the x limits of the axis.

    ylim: list or tuple (xmin,xmax)
          set the y limits of the axis.

    color_code: Python dictionary
                Array values to color code the points in the 2D plane.
                The keys are the labels for the color-coding. Shows up in a dropdown menu.
          
    cmap_plot: String. Default is 'Viridis'
               The color map used to color-code the x,y points with color_code values.

    marker_size: Integer. Default is 10
                 The size of the markers in the 2D plane.

    images: List of 3D arrays (N_points, N_pixe, N_pixel)
            A list of Images to be plotted.
            Can input several images for each object: images[0] should be a 3D array (N_points, N_pixe, N_pixel).

    cmap_images: String. Default is 'Viridis'
               The color map used for the images.

    image_labels: List of strings
                  A list that contains labels for images to be used for axis titles.
                  The list should be the same size as images list.
    
    Output
    ------
    Returns a Dash app
    '''
    
    app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

    if color_code is None:
        color_code = {'same for all': np.ones(len(list(x.values())))}

    fig = go.Figure()
    trace0 = go.Scatter(
        x=list(x.values())[0], y=list(y.values())[0],
        mode='markers',
        name='galaxies',
        marker=dict(
            size=marker_size,  # Change this value to adjust marker size
            color=list(color_code.values())[0],
            colorscale=cmap_plot,
            colorbar=dict(
                title=list(color_code.keys())[0], orientation='h'
            )
        )
    )
    fig.add_trace(trace0)

    fig.update_xaxes(title=list(x.keys())[0], range=xlim)
    fig.update_yaxes(title=list(y.keys())[0], range=ylim)
    fig.update_layout(width=750, height=650, font=dict(size=30))


    app.layout = html.Div([
        html.Div([
            dcc.Dropdown(
                options=[{'label': html.Span(k, style={'color': 'white'}), 'value': k} for k in color_code.keys()],
                value=list(color_code.keys())[0],
                id='color coding',
                style={'width': '50%', 'backgroundColor': '#2a2a2a'}
            )
        ]),
        html.Div([
            dcc.Graph(id='2d-scatter', figure=fig,
                      style={'display': 'inline-block'}, mathjax=True)
        ]),
        html.Div(
            html.Div(
                [dcc.Graph(id=image_labels[l], style={'display':'inline-block'}, mathjax=True) for l in range(len(images))]
            )
        )
    ])

    def create_images(ind):
        figs = []
        for i in range(len(images)):
            fig0 = px.imshow(images[i][ind,:,:], color_continuous_scale=cmap_images)
            #fig0.update_layout(title=str(ind), font=dict(size=30), title_x=0.5)
            figs.append(fig0)
        return figs

    @app.callback(
        [Output(image_labels[l], 'figure') for l in range(len(images))],
        Input('2d-scatter', 'hoverData')
    )
    def update_spectrum(hov_data):
        if hov_data is None:
            ind = 0
        else:
            ind = hov_data['points'][0]['pointIndex']
        return create_images(ind)

    @app.callback(
        Output('2d-scatter', 'figure'),
        Input('color coding', 'value')
    )
    def update_color_coding(color):
        fig = go.Figure()
        trace0 = go.Scatter(
            x=list(x.values())[0], y=list(y.values())[0],
            mode='markers',
            name='galaxies',
            marker=dict(
                size=marker_size,  # Change this value to adjust marker size
                color=list(color_code[color]),
                colorscale=cmap_plot,
                colorbar=dict(
                    title=color, orientation='h'
                )
            )
        )
        fig.add_trace(trace0)
        
        return fig

    return app

    

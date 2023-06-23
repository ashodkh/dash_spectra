import numpy as np
from jupyter_dash import JupyterDash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly

def dash_plot_images(x=None, y=None, xlim=None, ylim=None, color_code=None, cmap='Viridis', images=None,\
                      image_labels=None,\
                      kao_lines=False):
    '''
    Plotting function that uses Dash to plot galaxies in a 2d plane of properties and shows their spectra by hovering over the points.
    
    Input
    -----
    
    x,y : Python dictionaries
          The coordinates of the data points to be plotted. Can be anything measured for every galaxy, e.g. x=Mass, y=SFR. 
          Dictionary labels are the axis titles.

    xlim: list or tuple (xmin,xmax)
          set the x limits of the axis.

    ylim: list or tuple (xmin,xmax)
          set the y limits of the axis.

    color_code: Python dictionary
                Array values to color code the points in the 2D plane.
                The keys are the labels for the color-coding.

    cmap: String. Default is 'viridis'
          The color map used to color-code the x,y points with color_code values

    images: List of 3D arrays (N_pixe, N_pixel, N_points)
            A list of Images to be plotted. Can input several images for each object: images[0] should be a 3D array (N_pixe, N_pixel, N_points).

    image_labels: List of strings
                  A list that contains labels for images to be used for axis titles. The list should be the same size as images list.


    kao_lines: Boolean. Default is False.
               Adds kao lines to the 2D diagram.
    
    Output
    ------
    
    Returns a Dash app
    
    '''
        
    
    app = JupyterDash(__name__)

    if color_code is None:
        color_code = {'same for all': np.ones(len(list(x.values())))}
    fig = go.Figure()
    trace0 = go.Scatter(
        x=list(x.values())[0], y=list(y.values())[0],
        mode='markers',
        name='galaxies',
        marker=dict(
        color=list(color_code.values())[0],
        colorscale=cmap,
        colorbar=dict(
        title=list(color_code.keys())[0], orientation='h'
        )
        )
    )

    fig.add_trace(trace0)

    fig.update_traces(marker_size=3)
    fig.update_xaxes(title=list(x.keys())[0], range=xlim)
    fig.update_yaxes(title=list(y.keys())[0], range=ylim)
    fig.update_layout(width=750, height=650)


    app.layout = html.Div([html.Div([
        dcc.Graph(id='2d-scatter', figure=fig, style={'display': 'inline-block'})
    ]),
    html.Div(html.Div([dcc.Graph(id=image_labels[l], style={'display':'inline-block'}) for l in range(len(images))]))]
    )

    def create_images(ind):
        figs = []
        for i in range(len(images)):
            #trace = go.Scatter(x=wavelength, y=spectra[i][ind], mode='lines', marker=dict(color=spec_colors[i]), name=spec_names[i])
            #trace = go.Image(z=images[i][:,:,ind])
            #fig.add_trace(trace)
            fig0 = px.imshow(images[i][:,:,ind],color_continuous_scale='viridis')
            fig0.update_layout(title=str(ind))
            figs.append(fig0)

        return figs

    @app.callback(
        [Output(image_labels[l], 'figure') for l in range(len(images))],
        Input('2d-scatter', 'hoverData')
    )
    def update_spectrum(hov_data):
        ind = hov_data['points'][0]['pointIndex']
        return create_images(ind)

    return app

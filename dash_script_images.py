import numpy as np
from jupyter_dash import JupyterDash
from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import plotly

def dash_plot_images(x=None, y=None, xlim=None, ylim=None, color_code=None, cmap='Viridis', images=None,\
                      image_labels=None,\
                      kao_lines=False, masking=False, mask_ind=0):
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

    spectra: List of 2D arrays (N_points, N_features).
             A Python list of Spectra to be plotted. Can input several spectra for each object: spectra[0] should be a 2D array (N_points, N_features) that contains the first spectrum for every object (N_points) as a function of wavelnegth (N_features).
             So (N_points, N_features) = (number of galaxies, length of wavelength grid).

    wavelengths: 1-D array like.
                 The wavelength grid of the spectra.

    spec_colors: list (should be same length as the list of spectra)
                 Colors of the spectra. That is, if there are 2 spectra for each point, one possibility is spec_colors = ['blue', 'orange'].
                 Can also be input in rgb format: 'rgba(0,0,0,0.5)' is black with alpha=0.5, 'rgba(256,0,0,1)' is red with alpha=1, etc.

    spec_names: list (should be same length as the list of spectra)
                Names of the spectra. To be used as labels in Legend.

    zoom: Python dictionary.
          Locations in the spectrum to zoom in on. These will appear as separate subplots.
          The keys of the dictionary are labels for the subplots, and the values correspond to wavelengths to zoom in on.

    zoom_windows: Integer. Default=10
                  The zoom plots will have a wavelength range of wavelength[zoom-zoom_windows, zoom+zoom_windows]

    zoom_extras: List of Python dictionaries.
                 The list should be the size of zoom locations. There should be one dictionary for each zoom subplot.
                 The dictionaries contain extra values to add to zoom subplots. Can be shown in the legend or in the title.
                 Dictionary keys are the labels for the values.

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
            fig0 = px.imshow(np.log10(images[i][:,:,ind]))
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

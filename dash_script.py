import numpy as np
from dash import html, dcc, Input, Output, Dash
import plotly.graph_objects as go
import plotly
from dash_bootstrap_templates import load_figure_template
import dash_bootstrap_components as dbc

load_figure_template(["darkly"])


def dash_plot_spectra(x=None, y=None, xlim=None, ylim=None, color_code=None,
                      cmap='Tealgrn_r', spectra=None, spec_colors=plotly.colors.DEFAULT_PLOTLY_COLORS,
                      spec_names=['0'], wavelength=None, additional_lines=None,
                      masking=False, mask_ind=0, y_max=None, y_min=None,
                      zoom=None, zoom_windows=None, zoom_extras=None, zoom_extras_pos=None):
    '''
    Plotting function that uses Dash to plot galaxies in a 2d plane of
    properties and shows their spectra by hovering over the points.
    
    Input
    -----
    
    x,y : Python dictionaries
          The coordinates of the data points to be plotted. Can be anything
          measured for every galaxy, e.g. x=Mass, y=SFR.
          Dictionary labels are the axis titles.

    xlim: list or tuple (xmin,xmax)
          set the x limits of the axis.

    ylim: list or tuple (xmin,xmax)
          set the y limits of the axis.

    color_code: Python dictionary
                Array values to color code the points in the 2D plane.
                The keys are the labels for the color-coding.

    cmap: String. Default is 'viridis'
          The color map used to color-code the x,y points with color_code
          values.

    spectra: List of 2D arrays (N_points, N_features).
             A Python list of Spectra to be plotted. Can input several spectra
             for each object: spectra[0] should be a 2D array (N_points, N_features)
             that contains the first spectrum for every object (N_points)
             as a function of wavelnegth (N_features).
             So (N_points, N_features) = (number of galaxies, length of wavelength grid).

    wavelengths: List of 1D arrays(N_features).
                 The wavelength grid corresponding to the spectra.

    spec_colors: list (should be same length as the list of spectra)
                 Colors of the spectra. That is, if there are 2 spectra for
                 each point, one possibility is spec_colors = ['blue', 'orange'].
                 Can also be input in rgb format: 'rgba(0,0,0,0.5)' is black
                 with alpha=0.5, 'rgba(256,0,0,1)' is red with alpha=1, etc.

    spec_names: list (should be same length as the list of spectra)
                Names of the spectra. To be used as labels in Legend.

    zoom: Python dictionary.
          Locations in the spectrum to zoom in on.
          These will appear as separate subplots.
          The keys of the dictionary are labels for the subplots,
          and the values correspond to wavelengths to zoom in on.

    zoom_windows: Integer. Default=10
                  The zoom plots will have a wavelength range of
                  wavelength[zoom-zoom_windows, zoom+zoom_windows].

    zoom_extras: List of Python dictionaries.
                 The list should be the size of zoom locations.
                 There should be one dictionary for each zoom subplot.
                 The dictionaries contain extra values to add to zoom subplots.
                 Can be shown in the legend or in the title.
                 Dictionary keys are the labels for the values.

    additional_lines: Python list of dictionaries. Default=None.
                      Each object in the list is a dictionary with the keys.
                      x: 1D array (x values for the line to be plotted)
                      y: 1D array (y values for the line to be plotted)
                      color: String (color of the line)
                      line_dash: String (line style of the line)
                      name: String (name of the line to be shown in the legend)

    y_max: List of 1D arrays (N_points).
           Maximum flux value for each spectrum. 
           Used to set the y-axis range of the spectrum plot.
    
    y_min: List of 1D arrays (N_points).
           Minimum flux value for each spectrum.
           Used to set the y-axis range of the spectrum plot.
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
    fig.update_layout(width=750, height=650, font=dict(size=30))

    if additional_lines is not None:
        for i, additional_line in enumerate(additional_lines):
            trace1 = go.Scatter(
                x=additional_line['x'],
                y=additional_line['y'],
                marker_color=additional_line['color'],
                line_dash='solid' if additional_line['line_dash'] is None else additional_line['line_dash'],
                name=additional_line['name'],
                line=dict(width=10 if additional_line['line_width'] is None else additional_line['line_width'])
            )
            fig.add_trace(trace1)

    if zoom is not None:
        app.layout = html.Div([
            html.Div([
                dcc.Graph(id='2d-scatter', figure=fig,
                          style={'display': 'inline-block'}, mathjax=True),
                dcc.Graph(id='spectrum',
                          style={'display': 'inline-block'}, mathjax=True)
            ]),
            html.Div(html.Div([
                dcc.Graph(id=list(zoom.keys())[l],
                          style={'display': 'inline-block'}, mathjax=True)
                          for l in range(len(list(zoom.keys())))
                    ])
                )    
            ]
        )
    else:
        app.layout = html.Div([html.Div([
                dcc.Graph(id='2d-scatter', figure=fig,
                          style={'display': 'inline-block'}, mathjax=True),
                dcc.Graph(id='spectrum',
                          style={'display': 'inline-block'}, mathjax=True)
            ])
        ])

    def create_spectrum(ind, y_range=False):
        fig = go.Figure()
        for i in range(len(spectra)):
            trace = go.Scatter(x=wavelength[i], y=spectra[i][ind], mode='lines',
                               marker=dict(color=spec_colors[i]), name=spec_names[i])
            fig.add_trace(trace)

        fig.update_xaxes(title='Rest-Frame Wavelength (A)')
        fig.update_yaxes(title='flux')
        fig.update_layout(width=2000, height=650, font=dict(size=30))
        fig.update_layout(title='Spectrum vs Wavelength', title_x=0.5)

        if y_range:
            if y_max is not None:
                fig.update_layout(yaxis_range=[y_min[ind], y_max[ind]])

        return fig

    @app.callback(
        Output('spectrum', 'figure'),
        Input('2d-scatter', 'hoverData'))
    def update_spectrum(hov_data):
        if hov_data is None:
            ind = 0
        else:
            ind = hov_data['points'][0]['pointIndex']
        return create_spectrum(ind, y_range=True)
        
    if zoom is not None:
        @app.callback(
            [Output(list(zoom.keys())[l], 'figure') for l in range(len(list(zoom.keys())))],
            Input('2d-scatter', 'hoverData'))
        def update_lines(hov_data):
            if hov_data is None:
                ind = 0
            else:
                ind = hov_data['points'][0]['pointIndex']
            figs = []

            for l in range(len(list(zoom.keys()))):
                fig0 = create_spectrum(ind)
                fig0.update_xaxes(title='Wavelength (A)',
                                  range=[list(zoom.values())[l][ind]-zoom_windows[l],
                                         list(zoom.values())[l][ind]+zoom_windows[l]
                                         ]
                                  )
                fig0.update_layout(width=687.5, height=650, font=dict(size=30),
                                   showlegend=False)
                fig0.add_vline(x=list(zoom.values())[l][ind])
                fig0.update_layout(title=list(zoom.keys())[l], title_x=0.5)
                figs.append(fig0)

                if zoom_extras is not None:
                    string = ''
                    for j in range(len(list(zoom_extras[l].keys()))):
                        string += list(zoom_extras[l].keys())[j] +\
                                  f' {list(zoom_extras[l].values())[j][ind]:.2f} <br>'
                    fig0.update_layout(title=string, title_x=0.5)

            return figs

    return app

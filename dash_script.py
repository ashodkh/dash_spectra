import numpy as np
import pylab as plt
import scipy.signal
from matplotlib.backends.backend_pdf import PdfPages
from jupyter_dash import JupyterDash
from dash import html, dcc, Input, Output
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go

lines = ["O2_doub","HGAMMA_EW","HBETA_EW","OIII_4959_EW","OIII_5007_EW","NII_6548_EW"\
         ,"HALPHA_EW","NII_6584_EW","SII_6716_EW","SII_6731_EW", 'test']
lines_waves = [3728.5, 4342, 4862.7, 4960.3, 5008.2, 6549.9, 6564.6, 6585.3, 6718.3, 6732.7] 


def dash_plot_spectra(x=None, y=None, xlim=None, ylim=None, color_code=None, inds=None, spectra=None,\
                      spec_colors=None, spec_names=None, lines_to_zoom=None, line_ews_obs=None, obs_ivar=None, line_ews_fit=None, wavelength=None, zs=None,\
                      kao_lines=False, masking=False, mask_ind=0,\
                      zoom=None, zoom_windows=None, zoom_extras=None, zoom_extras_pos=None):
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

    inds: 1-D array like. Default is range(len(x)).
          array that matches x,y values to spectra indices. That is, the x[0], y[0] galaxy will have the spectrum spectra[inds[0]].
          Must be changed if x[0], y[0] does not correspond to spectra[0].

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

    zoom_extras: Python dictionary.
                 Extra values to add to zoom subplots. Can be shown in the legend or in the title.
                 Dictionary keys are the labels for the values.

    zoom_extras_pos: String. Default is 'legend'.
                     Where to put zoom_extras in the subplots. Can be 'legend' or 'title'.

    kao_lines: Boolean. Default is False.
               Adds kao lines to the 2D diagram.

    masking: Boolean. Default is False.
             Masks emission lines if True.

    
    Output
    ------
    
    Returns a Dash app
    
    '''
        
    
    app = JupyterDash(__name__)

    fig = go.Figure()
    trace0 = go.Scatter(
        x=list(x.values())[0], y=list(y.values())[0], customdata=np.stack((inds), axis=-1),
        mode='markers',
        name='galaxies',
        marker=dict(
        color=list(color_code.values())[0],
        colorscale='Viridis',
        colorbar=dict(
        title=list(color_code.keys())[0], orientation='h'
        )
        )
    )

    fig.add_trace(trace0)

    fig.update_xaxes(title=list(x.keys())[0], range=xlim)
    fig.update_yaxes(title=list(y.keys())[0], range=ylim)
    fig.update_layout(width=750, height=650)

    if kao_lines:
        x1 = np.arange(-2,0,0.1)
        x2 = np.arange(-2,0.21,0.1)

        trace1 = go.Scatter(x=x1, y=0.61/(x1+0.08) + 1.1, marker_color='black', name='star forming sequence')
        trace2 = go.Scatter(x=x1, y=0.61/(x1-0.05)+1.3, marker_color='magenta', name='ka03')
        trace3 = go.Scatter(x=x2, y=0.61/(x2-0.47)+1.19, marker_color='magenta', line_dash='dash', name='ka01')

        fig.add_trace(trace1)
        fig.add_trace(trace2)
        fig.add_trace(trace3)

    if zoom is not None:
        app.layout = html.Div([html.Div([
            dcc.Graph(id='2d-scatter', figure=fig, hoverData={'points': [{'customdata': [0]}]}, style={'display': 'inline-block'}),
            dcc.Graph(id='spectrum', style={'display': 'inline-block'})
        ]),
        html.Div(html.Div([dcc.Graph(id=list(zoom.keys())[l], style={'display':'inline-block'}) for l in range(len(list(zoom.keys())))]))]
        )
    else:
        app.layout = html.Div([html.Div([
            dcc.Graph(id='2d-scatter', figure=fig, hoverData={'points': [{'customdata': [0]}]}, style={'display': 'inline-block'}),
            dcc.Graph(id='spectrum', style={'display': 'inline-block'})
        ])]
        )

    def create_spectrum(ind):
        fig = go.Figure()
        for i in range(len(spectra)):
            trace = go.Scatter(x=wavelength, y=spectra[i][ind], mode='lines', marker=dict(color=spec_colors[i]), name=spec_names[i])
            fig.add_trace(trace)

        fig.update_xaxes(title='wavelength')
        fig.update_yaxes(title='flux')
        fig.update_layout(width=2000, height=650)

        return fig

    @app.callback(
        Output('spectrum', 'figure'),
        Input('2d-scatter', 'hoverData'))
    def update_spectrum(hov_data):
        return create_spectrum(hov_data['points'][0]['customdata'])
        
    if zoom is not None:
        @app.callback(
            [Output(list(zoom.keys())[l], 'figure') for l in range(len(list(zoom.keys())))],
            Input('2d-scatter', 'hoverData'))
        def update_lines(hov_data):
            ind = hov_data['points'][0]['customdata']
            figs = []
            # for i,l in enumerate(lines_to_zoom):
            #     fig0 = create_spectrum(ind)
            #     fig0.update_xaxes(title='wavelength', range=[lines_waves[l]*(1+zs[ind])-13,lines_waves[l]*(1+zs[ind])+13])
            #     fig0.update_layout(width=500, height=650)
            #     fig0.add_vline(x=lines_waves[l]*(1+zs[ind]))
            #     if line_ews_obs is None:
            #         fig0.update_layout(title=lines[l])# + f'={target_lines[l][ids[4]]:.2f}+-{line_ivars[l][ids[4]]:.2f}')
            #     else:
            #         fig0.update_layout(title=lines[l] + f' obs_EW={line_ews_obs[ind,l]:.2f} +- {1/np.sqrt(obs_ivar[ind,l]):.2f}' +'\n'+ f'fit_EW={line_ews_fit[ind,l]:.2f}')
            #     figs.append(fig0)

            for l in range(len(list(zoom.keys()))):
                fig0 = create_spectrum(ind)
                fig0.update_xaxes(title='wavelength', range=[list(zoom.values())[l][ind]-zoom_windows[l],list(zoom.values())[l][ind]+zoom_windows[l]])
                fig0.update_layout(width=500, height=650)
                fig0.add_vline(x=list(zoom.values())[l][ind])
                figs.append(fig0)

                fig0.update_layout(title=list(zoom.keys())[l])
                if zoom_extras is not None:
                    pass

            return figs

    return app

# dash_spectra

An example with DESI data is hosted on [https://dash-spectra.onrender.com/](https://dash-with-umap.onrender.com). It is quite slow online, so hosting it locally will be much faster.

dash_script.py is a Python module that contains a function to plot galaxies in 2D spaces (for example, mass and star formation rate) and shows the spectrum of each point that is hovered over in real-time. This is done using [Dash](https://dash.plotly.com/tutorial).

dash_script_images.py is a similar module but instead of showing spectra in real-time it shows images of the galaxies.

# Tutorial

The tutorial folder contains a Jupyter Notebook that demonstrates how to use this module with SDSS data. The data was obtained using [astroML](https://www.astroml.org/).

The output of the tutorial is hosted on https://dash-spectra.onrender.com/.

# Installation
dash_script.py is just a module that can be downloaded and placed in a directory. 

It has to be in a directory that can be recognized by Python. This can either be the directory where you're running the code, or in a directory that [Python knows the path of](https://stackoverflow.com/questions/4383571/importing-files-from-different-folder).

**Dependencies**
- Python
- [Dash, Jupyter Dash](https://dash.plotly.com/installation)
- [Plotly](https://plotly.com/python/getting-started/)
- [Numpy](https://numpy.org/install/)

# Acknowledgement 

This module was inspired by a 1-week session on Visualization that I had the pleasure of attending as part of the [LSST Data Science Fellowship Program](https://www.lsstcorporation.org/lincc/fellowship_program). 

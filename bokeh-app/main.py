
# This file is a free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This file is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# Copyright (C) 2019 Jeremie Houssineau
#
# Support: jeremie.houssineau AT warwick.ac.uk
#

import numpy as np

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import Slider, Button
from bokeh.plotting import figure


# Define p.d.f.s of interest

def normal_pdf(x, mu, var):
    return np.exp(-np.power(x-mu, 2)/(2*var)) / np.sqrt(2 * np.pi * var)

# True parameter
mu = 2
sigma_default = 1.0

# Number of points to plot the p.d.f.s (reduce this number of speed)
N = 250

x = np.linspace(-5, 5, N)
y = normal_pdf(x, 0.0, 1.0)
N0 = ColumnDataSource(data=dict(x=x, y=y))
N1 = ColumnDataSource(data=dict(x=x, y=y))

y = normal_pdf(x, mu, sigma_default**2)
N2 = ColumnDataSource(data=dict(x=x, y=y))

# Function regenerating the observations
max_n_obs = 10
obs_root = np.random.randn(max_n_obs)

y_obs = np.array((0,0.2))

button = Button(label="Regenerate observations")

# Set up plot
plot = figure(plot_height=400, plot_width=800, title="Prior, posterior and sampling distributions",
              tools="crosshair,pan,reset,save,wheel_zoom",
              x_range=[-5, 5], y_range=[0, 1.1])

plot.line('x', 'y', legend='prior', source=N0, line_width=3, line_alpha=0.6)
plot.line('x', 'y', source=N1, line_width=3, line_alpha=0.6, legend='posterior', line_dash='dashed')
plot.line('x', 'y', source=N2, line_width=3, line_alpha=0.6, legend='sampling', color='firebrick')

obs_data_list = []
obs_plot_list = []
for i in range(max_n_obs):
    obs = obs_root[i]*sigma_default + mu
    x_obs = obs*np.ones(2) 
    obs_data_list.append(ColumnDataSource(data=dict(x=x_obs, y=y_obs)))
    obs_plot_list.append(plot.line('x', 'y', source=obs_data_list[i],\
        color='firebrick', line_width=3, line_alpha=0.6))

# Set up widgets
mu_0 = Slider(title="mu_0", value=0.0, start=-5.0, end=5.0, step=0.1)
sigma_0 = Slider(title="sigma_0", value=1.0, start=0.01, end=5.0, step=0.1)
sigma = Slider(title="sigma", value=sigma_default, start=0.01, end=5.0, step=0.1)
n_obs = Slider(title="n", value=0, start=0, end=max_n_obs, step=1)

# Function modifying the x and y coordinates depending on the parameters
def update(attrname, old, new):
    mu_0_val = mu_0.value
    var_0 = sigma_0.value**2
    y = normal_pdf(x, mu_0_val, var_0)
    N0.data = dict(x=x, y=y)

    n = n_obs.value
    sig = sigma.value
    var = sig**2
    loc_obs = obs_root*sig + mu
    for i in range(max_n_obs):
        x_obs = loc_obs[i]*np.ones(2)
        if i < n:
            vis = True
        else:
            vis = False
        obs_data_list[i].data = dict(x=x_obs, y=y_obs)
        obs_plot_list[i].visible = vis
    
    if n == 0:
        obs = 0
    else:
        obs = np.mean(loc_obs[:n])

    mu_post = (n * var_0 * obs  + var * mu_0_val) / (n * var_0 + var)
    var_post = (var_0 * var) / (n * var_0 + var)
    y_post = normal_pdf(x, mu_post, var_post)
    
    N1.data = dict(x=x, y=y_post)

    y = normal_pdf(x, mu, var)
    N2.data = dict(x=x, y=y)

# Function regenerating the observations
def reg():
    global obs_root
    obs_root = np.random.randn(max_n_obs)
    update('value', 1, 1)

button.on_click(reg)

mu_0.on_change('value', update)
sigma_0.on_change('value', update)
sigma.on_change('value', update)
n_obs.on_change('value', update)

# Set up layouts and add to document
inputs = widgetbox(button, mu_0, sigma_0, sigma, n_obs)

curdoc().add_root(row(inputs, plot, width=800))
curdoc().title = "Normal likelihood: unknown mean"


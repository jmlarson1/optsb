#%%
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.io as pio
import math
from scipy import special
color = ['#31AFDB','#7F599A','#2AA590','#DB84B9','#A1A4A7','#E48E54','#DFBA23','#AD9B8F']
pio.templates["mycolor"] = go.layout.Template(
    layout_colorway=color)
pio.templates.default = "mycolor"

#%% data in
folder='/Users/calemhoffman/Research/anl/inflight/optsb/code/track/sps_line/'
fname=folder+'beam.out'
print(fname)
df_beam = pd.read_csv(fname,header=0,delim_whitespace=True)
df_beam.tail()
#%%
fname=folder+'coord.out'
df_coord = pd.read_csv(fname,header=0,delim_whitespace=True)
df_coord.tail()
#%%
fname=folder+'step.out'
df_step = pd.read_csv(fname,header=0,delim_whitespace=True)
df_step.tail()

#%%

fig_step = go.Figure()
quad_size=30.
for i in range(3):
    fig_step.add_shape(type="rect",x0=df_beam['dist[m]'].values[i*2+2]*100-quad_size, 
    y0=0, x1=df_beam['dist[m]'].values[i*2+2]*100, y1=3,
    line=dict(width=0),fillcolor=color[6],opacity=0.25,layer='below'
    )

fig_step.add_trace(go.Scatter(name='X-rms',x=df_step['z[cm]'], 
y=df_step['Y-rms[cm]'],mode='lines',marker_color=color[0],
fill='tozeroy'))

fig_step.add_trace(go.Scatter(name='Y-rms',x=df_step['z[cm]'], 
y=df_step['X-rms[cm]'],mode='lines',marker_color=color[1],
fill='tozeroy'))

fig_step.add_trace(go.Scatter(name='X-max',x=df_step['z[cm]'], 
y=df_step['Y-max[cm]'],mode='lines',marker_color=color[0],
line_dash='dot'))

fig_step.add_trace(go.Scatter(name='Y-max',x=df_step['z[cm]'], 
y=df_step['X-max[cm]'],mode='lines',marker_color=color[1],
line_dash='dot'))

# fig_step.add_trace(go.Scatter(x=df_beam['dist[m]']*100., 
#                     y=df_beam['x_rms[cm]'],mode='markers',
#                     marker_symbol=1,marker_color=color[0]))
# fig_step.add_trace(go.Scatter(x=df_beam['dist[m]']*100., 
#                     y=df_beam['y_rms[cm]'],mode='markers',
#                     marker_symbol=1,marker_color=color[1]))

fig_step.update_xaxes(title="distance [cm]",range=[0,900])
fig_step.update_yaxes(title="size [cm]",range=[0,3])

fig_step.show()
#%%
fig_coord = make_subplots(2,2)

#traces
fig_coord.add_trace(go.Scatter(x=df_coord['dW[MeV/u]'], 
y=df_coord['dt[nsec]'],mode='markers'),row=1,col=1)

fig_coord.add_trace(go.Scatter(x=df_coord['x[cm]'], 
y=df_coord['x\'[mrad]'],mode='markers'),row=1,col=2)

fig_coord.add_trace(go.Scatter(x=df_coord['y[cm]'], 
y=df_coord['y\'[mrad]'],mode='markers'),row=2,col=1)

fig_coord.add_trace(go.Scatter(x=df_coord['x[cm]'], 
y=df_coord['y[cm]'],mode='markers'),row=2,col=2)

# Update xaxis properties
fig_coord.update_xaxes(title_text="dW[MeV/u]", range=[-0.5, 0.5], row=1, col=1)
fig_coord.update_xaxes(title_text="x[cm]", range=[-2, 2], row=1, col=2)
fig_coord.update_xaxes(title_text="y[cm]", range=[-2, 2], row=2, col=1)
fig_coord.update_xaxes(title_text="x[cm]", range=[-2, 2], row=2, col=2)

# Update yaxis properties
fig_coord.update_yaxes(title_text="dt[nsec]", range=[-3,3], row=1, col=1)
fig_coord.update_yaxes(title_text="x\'[mrad]", range=[-10,10], row=1, col=2)
fig_coord.update_yaxes(title_text="y\'[mrad]", range=[-10,10], row=2, col=1)
fig_coord.update_yaxes(title_text="y[cm]", range=[-2, 2], row=2, col=2)

fig_coord.update_layout(title='coordinate plots [target]',width=600,height=600,showlegend=False)

fig_coord.show()
# %%

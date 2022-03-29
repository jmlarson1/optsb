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
#color = px.colors.sequential.Plotly3
color = ['#31AFDB','#7F599A','#2AA590','#DB84B9','#A1A4A7','#E48E54','#DFBA23','#AD9B8F']
#color = ['#6B313F','#C7B486','#555555','#000000','#6B313F','#C7B486','#555555','#000000']

pio.templates["mycolor"] = go.layout.Template(
    layout_colorway=color)
pio.templates.default = "mycolor"

#%% data in
df_beam = pd.read_csv('../example/out_compare/beam.out',header=0,delim_whitespace=True)
df_beam.tail()
#%%
df_coord = pd.read_csv('../example/out_compare/coord.out',header=0,delim_whitespace=True)
df_coord.tail()
# %%
fig = go.Figure()
fig.add_trace(go.Scatter(x=df_beam['dist[m]'], y=df_beam['x_rms[cm]'],mode='lines'))
fig.add_trace(go.Scatter(x=df_beam['dist[m]'], y=df_beam['y_rms[cm]'],mode='lines'))
fig.add_trace(go.Scatter(x=df_beam['dist[m]'], y=df_beam['Xmax[cm]'],mode='lines'))
fig.add_trace(go.Scatter(x=df_beam['dist[m]'], y=df_beam['Ymax[cm]'],mode='lines'))

fig.show()
#%%
fig = make_subplots(2,2)
fig.add_trace(go.Scatter(x=df_coord['dW[MeV/u]'], y=df_coord['dt[nsec]'],mode='markers'),row=1,col=1)
fig.add_trace(go.Scatter(x=df_coord['x[cm]'], y=df_coord['x\'[mrad]'],mode='markers'),row=1,col=2)
fig.add_trace(go.Scatter(x=df_coord['y[cm]'], y=df_coord['y\'[mrad]'],mode='markers'),row=2,col=1)
fig.show()
# %%

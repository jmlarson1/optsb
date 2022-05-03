#%%
import os
import subprocess
from datetime import datetime
from random import random
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import plotly.io as pio
import math
from scipy import special
color = ['#31AFDB','#7F599A','#2AA590','#DB84B9',
        '#A1A4A7','#E48E54','#DFBA23','#AD9B8F']
pio.templates["mycolor"] = go.layout.Template(
    layout_colorway=color)
pio.templates.default = "mycolor"

from run_track import RunTRACK

#%% MAIN
df_results = pd.DataFrame()
quad_vals = []
run_with_testing = 1
rs = RunTRACK()

for i in range(10):
    run_dir = rs.set_dir()
    quad_vals = rs.get_quad_vals() #[1100,-1900,1200]
    print(quad_vals)
    rs.set_track(run_dir,quad_vals)
    rs.run_track(run_dir)
    df_beam,df_coord,df_step = rs.get_output(run_dir)
    rs.plot_track(df_beam,df_coord,df_step,quad_vals)
    df_temp = {'run_dir' : run_dir,
    'Q1': quad_vals[0], 'Q2': quad_vals[1], 'Q3': quad_vals[2],
    'Xrms': df_beam['x_rms[cm]'].values[len(df_beam.index)-1], 
    'Yrms': df_beam['y_rms[cm]'].values[len(df_beam.index)-1],
    'ax': df_beam['a_x'].values[len(df_beam.index)-1], 
    'ay': df_beam['a_y'].values[len(df_beam.index)-1],
    'az': df_beam['a_z'].values[len(df_beam.index)-1],
    'part_lost': df_beam['#of_part_lost'].values[len(df_beam.index)-1],
    'part_left': df_beam['#of_part_left'].values[len(df_beam.index)-1]
    }
    df_results = df_results.append(df_temp, ignore_index = True)

df_results.tail
#
# plot_results(df_results)
#%%
df_beam.columns
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=df_results['Q1']/-df_results['Q2'], 
    y=df_results['Q3']/-df_results['Q2'],
    # x=df_results['ax'], 
    # y=df_results['ay'],
    mode='markers',marker_color=1./(df_results['Xrms']+df_results['Yrms']),
    marker_size=(df_results['part_left']/100.)
    ))

fig.update_xaxes(title="Q1/Q2",range=[0,2])
fig.update_yaxes(title="Q3/Q2",range=[0,2])
fig.show()
# %%

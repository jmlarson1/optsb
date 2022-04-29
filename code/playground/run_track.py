#%% code to execute track and save in new dir (working off pyTRACK codes)
import os
import subprocess
from datetime import datetime
from random import random

import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objs import Scatter
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
import plotly.io as pio
import math
from scipy import special
color = ['#31AFDB','#7F599A','#2AA590','#DB84B9','#A1A4A7','#E48E54','#DFBA23','#AD9B8F']
pio.templates["mycolor"] = go.layout.Template(
    layout_colorway=color)
pio.templates.default = "mycolor"

track_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/build/"
track_exe="TRACKv39C.exe"
base_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/sps_line/"

current_dir = os.getcwd()
print(current_dir)
print(int(datetime.utcnow().strftime("%Y%m%d%H%M%S")))

#%% start of loop
# mkdir new run dir w/ date or number
def set_dir():
    date_time = int(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
    run_dir = os.path.join(base_dir, f"sim_{date_time}")
    print(run_dir)
    if (os.path.isdir(run_dir)):
        print("directory exists")
    else:
        os.mkdir(run_dir)
    return run_dir

#%%
#cp track input files
def set_track(run_dir,quad_vals):
    track_input_files = ['track.dat','sclinac.dat','fi_in.dat']
    for file_name in track_input_files:
        cp_file1 = os.path.join(base_dir,file_name)
        cp_file2 = os.path.join(run_dir,file_name)
        print(cp_file1)
        os.system(f"cp {cp_file1} {cp_file2}")
    #modify track input files as needed
    sclinac_file = os.path.join(run_dir, "sclinac.dat")
    with open(sclinac_file, "r") as file:
        lines = file.readlines()
        n_quad = 0
        for i, line in enumerate(lines):
            if "quad" in line:
                split_line = line.split()
                split_line[2] = str(quad_vals[n_quad])
                lines[i] = " ".join(split_line) + "\n"
                n_quad += 1
                # print(lines[i])
    with open(sclinac_file, "w") as file:
        file.writelines(lines)


# %%
# push new data to database, pull info to plot etc. location??
def plot_track(run_dir):
    fname=run_dir+'/beam.out'
    df_beam = pd.read_csv(fname,header=0,delim_whitespace=True)
    fname=run_dir+'/coord.out'
    df_coord = pd.read_csv(fname,header=0,delim_whitespace=True)
    fname=run_dir+'/step.out'
    df_step = pd.read_csv(fname,header=0,delim_whitespace=True)

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

    fig_step.update_xaxes(title="distance [cm]",range=[0,900])
    fig_step.update_yaxes(title="size [cm]",range=[0,3])

    #fig_step.show()
    fig_step.write_image("profile.png")

#%%
def get_quad_vals():
    quad_vals = [1150,-1800,1000]
    quad_vals[0] = random()*2000.
    quad_vals[1] = random()*(-2000.)
    quad_vals[2] = random()*2000.
    return quad_vals

#%%
#mv to new run directory & exec track
def run_track():
    run_dir = set_dir()
    quad_vals = get_quad_vals() #[1100,-1900,1200]
    print(quad_vals)
    set_track(run_dir,quad_vals)
    os.chdir(run_dir)
    completed = subprocess.call(
        "wine64 " + str(os.path.join(track_dir, track_exe)), shell=True
    )
    plot_track(run_dir)
    os.listdir()
#%%

run_track()

#%%
print(random())

#%% go back to working dir
os.chdir(current_dir)

# %%

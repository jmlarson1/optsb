#%% code to execute track and save in new dir (working off pyTRACK codes)
import os
import subprocess
from datetime import datetime
from random import random
import time

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

class RunTRACK():
    def __init__(self):
        self.run_with_testing = 1
        self.run_dir = ""
        self.track_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/build/"
        self.track_exe="TRACKv39C.exe"
        self.base_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/sps_line/"
        self.current_dir = os.getcwd()
        print(self.current_dir)
        print(int(datetime.utcnow().strftime("%Y%m%d%H%M%S")))

    # mkdir new run dir w/ date or number
    def set_dir(self):
        if (self.run_with_testing == 1):
            self.run_dir = os.path.join(self.base_dir, "testing")
        else:
            time.sleep(1.5) #needed to be sure new folder is made for loop
            date_time = int(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
            self.run_dir = os.path.join(self.base_dir, f"sim_{date_time}")
        print(self.run_dir)
        if (os.path.isdir(self.run_dir)):
            print("directory exists")
        else:
            os.mkdir(self.run_dir)
        return self.run_dir

    def set_track(self,run_dir,quad_vals):
        track_input_files = ['track.dat','sclinac.dat','fi_in.dat']
        for file_name in track_input_files:
            cp_file1 = os.path.join(self.base_dir,file_name)
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

    def plot_track(self,df_beam,df_coord,df_step,quad_vals):
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
        fig_step.add_annotation(showarrow=False,x=400,y=3.5,
        text="Q1 {:.3f}, Q2 {:.3f}, Q3 {:.3f}".format(quad_vals[0],quad_vals[1],quad_vals[2]))
        fig_step.update_xaxes(title="distance [cm]",range=[0,900])
        fig_step.update_yaxes(title="size [cm]",range=[0,4])
        fig_step.write_image("profile.png")

    def get_quad_vals(self):
        quad_vals = [1150,-1800,1000]
        quad_vals[0] = random()*2000.
        quad_vals[1] = random()*(-2000.)
        quad_vals[2] = random()*2000.
        return quad_vals

    def get_output(self,run_dir):
        fname=run_dir+'/beam.out'
        df_beam = pd.read_csv(fname,header=0,delim_whitespace=True)
        #print(df_beam.tail)
        fname=run_dir+'/coord.out'
        df_coord = pd.read_csv(fname,header=0,delim_whitespace=True)
        fname=run_dir+'/step.out'
        df_step = pd.read_csv(fname,header=0,delim_whitespace=True)
        return df_beam,df_coord,df_step

    def run_track(self,run_dir):
        os.chdir(run_dir)
        completed = subprocess.call(
            "wine64 " + str(os.path.join(self.track_dir, self.track_exe)), shell=True
        )
        os.listdir()

# #%% MAIN
# df_results = pd.DataFrame()
# quad_vals = []
# run_with_testing = 1
# rs = RunTRACK()

# for i in range(10):
#     run_dir = rs.set_dir()
#     quad_vals = rs.get_quad_vals() #[1100,-1900,1200]
#     print(quad_vals)
#     rs.set_track(run_dir,quad_vals)
#     rs.run_track(run_dir)
#     df_beam,df_coord,df_step = rs.get_output(run_dir)
#     rs.plot_track(df_beam,df_coord,df_step,quad_vals)
#     df_temp = {'run_dir' : run_dir,
#     'Q1': quad_vals[0], 'Q2': quad_vals[1], 'Q3': quad_vals[2],
#     'Xrms': df_beam['x_rms[cm]'].values[len(df_beam.index)-1], 
#     'Yrms': df_beam['y_rms[cm]'].values[len(df_beam.index)-1],
#     'ax': df_beam['a_x'].values[len(df_beam.index)-1], 
#     'ay': df_beam['a_y'].values[len(df_beam.index)-1],
#     'az': df_beam['a_z'].values[len(df_beam.index)-1],
#     'part_lost': df_beam['#of_part_lost'].values[len(df_beam.index)-1],
#     'part_left': df_beam['#of_part_left'].values[len(df_beam.index)-1]
#     }
#     df_results = df_results.append(df_temp, ignore_index = True)

# df_results.tail
# #
# # plot_results(df_results)
# #%%
# df_beam.columns
# fig = go.Figure()
# fig.add_trace(go.Scatter(
#     x=df_results['Q1']/-df_results['Q2'], 
#     y=df_results['Q3']/-df_results['Q2'],
#     # x=df_results['ax'], 
#     # y=df_results['ay'],
#     mode='markers',marker_color=1./(df_results['Xrms']+df_results['Yrms']),
#     marker_size=(df_results['part_left']/100.)
#     ))

# fig.update_xaxes(title="Q1/Q2",range=[0,2])
# fig.update_yaxes(title="Q3/Q2",range=[0,2])
# fig.show()

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
        self.doShowPlot = False
        self.run_with_testing = 1
        self.run_dir = ""
        #make below 'more' generic
        self.current_dir = os.getcwd()
        self.main_dir, temp = os.path.split(os.getcwd()) #assumes working from playground dir
        #print(self.main_dir)
        if (temp == "playground"):
            self.track_dir = self.main_dir + "/track/build/"
            self.base_dir = self.main_dir + "/track/sps_line/"
        else:
            self.main_dir, _ = os.path.split(self.main_dir)
            self.track_dir = self.main_dir + "/build/"
            self.base_dir = self.main_dir + "/sps_line/"
        #print(self.base_dir)
        self.track_exe="TRACKv39C.exe"
        #print(int(datetime.utcnow().strftime("%Y%m%d%H%M%S")))

    # mkdir new run dir w/ date or number
    def set_dir(self):
        if (self.run_with_testing == 1):
            self.run_dir = os.path.join(self.base_dir, "testing")
        else:
            time.sleep(1.5) #needed to be sure new folder is made for loop
            date_time = int(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
            self.run_dir = os.path.join(self.base_dir, f"sim_{date_time}")
        #print(self.run_dir)
        if (os.path.isdir(self.run_dir)):
            print("directory exists")
        else:
            os.mkdir(self.run_dir)
        return self.run_dir

    def set_track(self,run_dir,quad_vals):
        print("quad_vals: {}".format(quad_vals))
        track_input_files = ['track.dat','sclinac.dat','fi_in.dat']
        for file_name in track_input_files:
            cp_file1 = os.path.join(self.base_dir,file_name)
            cp_file2 = os.path.join(run_dir,file_name)
            #print(cp_file1)
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
        if (self.doShowPlot):
            fig_step.show()

    def mod_quad_vals(self,action,quad_vals):
        dt_size = 50. # units to change quad vals
        dt_dir = [1., -1., 0.]
        dt = []
        dt.append(sum(action[0:3])*dt_dir[np.argmax(action[:3])])
        dt.append(sum(action[3:6])*dt_dir[np.argmax(action[3:6])])
        dt.append(sum(action[6:9])*dt_dir[np.argmax(action[6:9])])
        print("dt values: {}".format(dt))
        #quad_vals = [0.,0.,0.]
        if (sum(action) == 0):
            quad_vals[0] = random()*2000.
            quad_vals[1] = random()*(-2000.)
            quad_vals[2] = random()*2000.
        else:
            for i in range(3):
                quad_vals[i] = quad_vals[i] + dt_size * dt[i]
            # tmp_np = np.array(quad_vals)
            # tmp_np[tmp_np > 2000.] = 2000. 
            # tmp_np[tmp_np < -2000.] = -2000. 
            # quad_vals = list(tmp_np)
        return quad_vals

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


# %%

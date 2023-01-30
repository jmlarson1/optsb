#%%
import os
import sys
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
# color = ['#983A38','#BF4D3B','#423155','#7F4772',
#         '#1D220F','#435F2B','#C4B690','#000000']
color = ['#5495EF','#6EB887','#CE5F4E','#EB9F47',
        '#E2E2E2','#506173','#ad7fa8','#000000']
pio.templates["mycolor"] = go.layout.Template(
    layout_colorway=color)
pio.templates.default = "mycolor"

from run_track import RunTRACK

#%% MAIN
#thetai_name="12"
thetai_names=["01","02","03","04","05","06","07","08","09","10","11","12"]
brho_id = [0,1,2,3,4,5,6,7,8,9,10,11]
# thetai_names=["03","06","09"]
# brho_id = [2,5,8]
brho_new = [0.996948,0.767466,0.802228,1.435824,0.757459,0.655691,
            1.15592,0.768313,0.633925,0.984128,1.028494,1.067932]
brho_old = brho_new[0]#0.996948

run_with_testing = 1

for i in range(len(thetai_names)):
    #pb
    quad_vals0 = [1047.11530,-1869.9161,1111.93598,766.9317,-700.68,-378.23,404.216,-192.6798,233.0581,-218.43955,465.59886,-203.72080]
    #sb
    #quad_vals0 = [821.36,-2544.29,1600.84,649.23,-626.93,-289.37,329.70,-138.49,182.95,-134.68,383.03,-153.00]
    quad_vals = quad_vals0
    folder_location="transport_line/theta_"+thetai_names[i]
    #folder_location="sps_line/testing"
    df_results = pd.DataFrame()
    rs = RunTRACK(folder_location)
    for j in range(len(quad_vals0)):
        quad_vals[j] = quad_vals0[j]*brho_new[brho_id[i]]/brho_old
    print(quad_vals)
    rs.mod_track(quad_vals)
    rs.run_track()
    df_beam,df_coord,df_step = rs.get_output()
    rs.plot_track(df_beam,df_coord,df_step)
    print(df_beam.tail)
    print("done with one loop")
print("exiting...now")
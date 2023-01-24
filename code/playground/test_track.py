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
thetai_names=["01","02"]
quad_vals0 = [-5400.,4470.,-3000.,875.,-1150.,1077.,-1130.,-717.,535.,737.,-1500.,856.]
quad_vals = quad_vals0
brho_new = 1.0
run_with_testing = 1

for i in range(len(thetai_names)):
    folder_location="transport_line/theta_"+thetai_names[i]
    #folder_location="sps_line/testing"
    df_results = pd.DataFrame()
    rs = RunTRACK(folder_location)
    #quad_vals=[-5940.00,4282.77,-2460.00,517.26,-1150.00,1617.00,-590.00,-1257.00,0.00,185.02,-2039.90,327.88]
    for j in range(len(quad_vals0)):
        quad_vals[i] = quad_vals0[i]*brho_new
    rs.mod_track(quad_vals)
    rs.run_track()
    df_beam,df_coord,df_step = rs.get_output()
    rs.plot_track(df_beam,df_coord,df_step)
    print(df_beam.tail)
    print("done with one loop")
print("exiting...now")
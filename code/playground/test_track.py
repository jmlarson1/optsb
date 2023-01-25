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
thetai_names=["01"]
brho_id = [0,3,6]
brho_new = [0.996948,0.767466,0.802228,1.435824,0.757459,0.655691,
            1.15592,0.768313,0.633925,0.984128,1.028494,1.067932]
brho_old = 0.996948
#quad_vals0 = [-5400.,4470.,-3000.,875.,-1150.,1077.,-1130.,-717.,535.,737.,-1500.,856.]
quad_vals0 = [-1021.35000,1044.68712,-983.08040,285.21116,-719.28507,384.04396 ,-599.98769,-186.35284,238.77694,215.00059,-465.59886,203.72080]
quad_vals = quad_vals0
run_with_testing = 1

for i in range(len(thetai_names)):
    #quad_vals0 = [-1000.,1000.,-1000.,200.,-500.,200.,-500.,-200.,200.,200.,-500.,200.]
    quad_vals0 = [-1021.35000,1044.68712,-983.08040,285.21116,-719.28507,384.04396 ,-599.98769,-186.35284,238.77694,215.00059,-465.59886,203.72080]
    folder_location="transport_line/theta_"+thetai_names[i]
    #folder_location="sps_line/testing"
    df_results = pd.DataFrame()
    rs = RunTRACK(folder_location)
    #quad_vals=[-5940.00,4282.77,-2460.00,517.26,-1150.00,1617.00,-590.00,-1257.00,0.00,185.02,-2039.90,327.88]
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
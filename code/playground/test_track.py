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

#%% MAIN transport line
# CHOOSE WITH THETA_## from 01 to 12
thetai_name="06"

folder_location="transport_line/theta_"+thetai_name
#folder_location="transport_line/testing"
df_results = pd.DataFrame()
run_with_testing = 1
rs = RunTRACK(folder_location)
#quad_vals = [-5400.,4470.,-3000.,875.,-1150.,1077.,-1130.,-717.,535.,737.,-1500.,856.]
#rs.mod_track(quad_vals)
rs.run_track()
df_beam,df_coord,df_step = rs.get_output()
rs.plot_track(df_beam,df_coord,df_step)
print(df_beam.tail)
print("exiting...now")
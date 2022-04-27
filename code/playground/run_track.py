#%% code to execute track and save in new dir (working off pyTRACK codes)
import os
import subprocess
from datetime import datetime

track_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/build/"
track_exe="TRACKv39C.exe"
base_dir="/Users/calemhoffman/Research/anl/inflight/optsb/code/track/sps_line/"

#%%
current_dir = os.getcwd()
print(current_dir)

#%%
print(int(datetime.utcnow().strftime("%Y%m%d%H%M%S")))

#%%
# mkdir new run dir w/ date or number
date_time = int(datetime.utcnow().strftime("%Y%m%d%H%M%S"))
run_dir = os.path.join(base_dir, f"sim_{date_time}")
print(run_dir)

#%%
if (os.path.isdir(run_dir)):
    print("directory exists")
else:
    os.mkdir(run_dir)

#%%
#cp track input files
track_input_files = ['track.dat','sclinac.dat','fi_in.dat']
for file_name in track_input_files:
    cp_file1 = os.path.join(base_dir,file_name)
    cp_file2 = os.path.join(run_dir,file_name)
    print(cp_file1)
    os.system(f"cp {cp_file1} {cp_file2}")

#%%
#modify track input files as needed
quad_vals = [1100,-1900,1200]
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

#%%
#mv to new run directory & exec track
os.chdir(run_dir)
completed = subprocess.call(
    "wine " + str(os.path.join(track_dir, track_exe)), shell=True
)
# %%
# push new data to database, pull info to plot etc. location??

#%% go back to working dir
os.chdir(current_dir)

# %%

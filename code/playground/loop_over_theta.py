import os
import pandas as pd

from run_track import RunTRACK

for i in range(12):
    starting_dir = os.getcwd()

    thetai_name = f"{i+1:02d}"  # pad with one zero
    folder_location = "transport_line/theta_" + thetai_name

    df_results = pd.DataFrame()
    rs = RunTRACK(folder_location)
    # quad_vals = [-5400.0, 4470.0, -3000.0, 875.0, -1150.0, 1077.0, -1130.0, -717.0, 535.0, 737.0, -1500.0, 856.0]
    # rs.mod_track(quad_vals)
    rs.run_track()
    df_beam, df_coord, df_step = rs.get_output()
    print(df_beam.iloc[-1]["#of_part_left"])

    os.chdir(starting_dir)

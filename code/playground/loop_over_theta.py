import os
import sys
import pandas as pd
import numpy as np

from run_track import RunTRACK

def obj_fun_with_DB(quad_vals):
    m = 12
    fvec = np.zeros(m)
    database = "theta_i_part_left_database.npy"
    DB = []
    for i in range(m):
        match = 0
        if os.path.exists(database):
            DB = np.load(database, allow_pickle=True)
            for db_entry in DB:
                if db_entry["theta_i"] == i and np.allclose(db_entry["var_vals"], quad_vals, rtol=1e-12, atol=1e-12):
                    fval = db_entry["#of_part_left"]
                    match = 1
                    break

        if match == 0:
            # Do the sim
            starting_dir = os.getcwd()
            thetai_name = f"{i+1:02d}"  # pad with one zero
            folder_location = "transport_line/theta_" + thetai_name
            df_results = pd.DataFrame()
            rs = RunTRACK(folder_location)
            rs.mod_track(quad_vals)
            rs.run_track()
            df_beam, df_coord, df_step = rs.get_output()
            os.chdir(starting_dir)

            fval = df_beam.iloc[-1]["#of_part_left"]

            to_save = {"#of_part_left": fval, "theta_i": i, "var_vals": quad_vals}
            DB = np.append(DB, to_save)
            np.save(database, DB)

        fvec[i] = fval

    # return 10000 - fvec
    return fvec

if __name__ == "__main__":
    # quad_vals = [-5400.0, 4470.0, -3000.0, 875.0, -1150.0, 1077.0, -1130.0, -717.0, 535.0, 737.0, -1500.0, 856.0]
    quad_vals = sys.argv[1:]
    quad_vals = [float(i) for i in quad_vals]
    fvec = obj_fun_with_DB(quad_vals)
    np.savetxt('fvec.out', fvec)

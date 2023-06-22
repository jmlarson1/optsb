import os
import sys
import pandas as pd
import numpy as np

from run_track import RunTRACK

def obj_fun_with_DB(quad_vals, i, npat):
    # because ParMOO has its special class for design points

    rigid = np.loadtxt('rigidity.txt')

    quad_vals = np.array([quad_val for quad_val in quad_vals])
    quad_vals = rigid[i-1] * quad_vals

    database = "theta_" + str(i) + "_database_" + str(npat) +".npy"
    DB = []
    match = 0
    if os.path.exists(database):
         DB = np.load(database, allow_pickle=True)
         for j, db_entry in enumerate(DB):
                 if np.allclose(db_entry["var_vals"], quad_vals, rtol=1e-12, atol=1e-12):
                     fval = db_entry["f"]
                     match = 1
                     print("match found")
                     break

    if match == 0:
        # Do the sim
        starting_dir = os.getcwd()
        thetai_name = f"{i:02d}"  # pad with one zero
        folder_location = "transport_line/theta_" + thetai_name
        df_results = pd.DataFrame()
        rs = RunTRACK(folder_location)
        rs.mod_track(quad_vals)
        rs.run_track()
        df_beam, df_coord, df_step = rs.get_output()
        os.chdir(starting_dir)

        #x = df_coord["x[cm]"].to_numpy()
        #y = df_coord["y[cm]"].to_numpy()
        fval = df_beam.iloc[-1]["#of_part_left"]
        #fval = np.hstack((x,y))

        to_save = {"f": fval, "var_vals": quad_vals}
        DB = np.append(DB, to_save)
        np.save(database, DB, allow_pickle=True)

    return fval

if __name__ == "__main__":
    nargin = len(sys.argv)
    quad_vals = sys.argv[1:nargin-2]
    quad_vals = [float(i) for i in quad_vals]
    i = int(sys.argv[nargin-2])
    npat = int(sys.argv[nargin-1])
    fvec = obj_fun_with_DB(quad_vals, i, npat)
    np.savetxt('fvec.out', np.reshape(fvec, -1))

    

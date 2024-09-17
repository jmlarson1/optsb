from run_track import RunTRACK
import numpy as np

import sys
sys.path.insert(0, '/home/mmenickelly/IBCDFO/pounders/py/')
sys.path.insert(0, '/home/mmenickelly/IBCDFO/minq/py/minq5/')
#sys.path.insert(0, '/home/jmlarson/research/poptus/IBCDFO/pounders/py/')
#sys.path.insert(0, '/home/jmlarson/research/poptus/IBCDFO/minq/py/minq5/')
from pounders import *
# from pounders import pounders

from single_theta import obj_fun_with_DB

def obj_fun(x):
    # print(x)
    # rs = RunTRACK()
    # run_dir = rs.set_dir()
    # quad_vals = list(x.squeeze())
    # print(quad_vals)
    # rs.set_track(run_dir, quad_vals)
    # rs.run_track(run_dir)
    # df_beam, df_coord, df_step = rs.get_output(run_dir)
    # x = df_coord["x[cm]"].to_numpy()
    # y = df_coord["y[cm]"].to_numpy()
    # out = np.hstack((x,y))

    # import ipdb; ipdb.set_trace()
    # SECOND ARG: which theta, THIRD ARG: how many npat
    print("x = ",x)
    out = obj_fun_with_DB(x, 2, 5000)
    print("length of F = ", len(out))
    #sys.exit('a')
    return out

if __name__ == "__main__":
    #import ipdb; ipdb.set_trace()
    # x = np.array([[1098.47, -1985.25, 1242.06]])
    x = np.array([720.99624333, -1896.45344981,  1656.26142883])

    # x =  [1047.,-1869.,1111,766.9317,-700.68,-378.23,404.216,-192.6798,233.0581,-218.43955,465.59886,-203.72080];
    y = obj_fun(x)

    n = 3
    X0 = x
    # mpmax [int] Maximum number of interpolation points (>n+1) (2*n+1)
    mpmax = 2 * n + 1
    # nfmax   [int] Maximum number of function evaluations (>n+1) (100)
    nfmax = 100
    # gtol [dbl] Tolerance for the 2-norm of the model gradient (1e-4)
    gtol = 10 ** -13
    # delta [dbl] Positive trust region radius (.1)
    delta = 100.0
    # nfs  [int] Number of function values (at X0) known in advance (0)
    nfs = 0
    # m [int] number of residuals
    m = 9950 #10002 
    # F0 [dbl] [fstart-by-1] Set of known function values  ([])
    F0 = []
    # xind [int] Index of point in X0 at which to start from (0)
    xind = 0
    # Low [dbl] [1-by-n] Vector of lower bounds (-Inf(1,n))
    Low = np.array([[0, -2500, 0]])
    # Upp [dbl] [1-by-n] Vector of upper bounds (Inf(1,n))
    Upp = np.array([[2500, 0, 2500]])
    printf = True

    # np.random.seed(0)
    # reps = 1000
    # X = np.random.uniform(Low,Upp,(reps,3))
    # y = np.zeros(reps)
    # best = 1e8
    # for i,x in enumerate(X):
    #     out = np.sum(obj_fun(x)**2)
    #     y[i] = out
    #     if out < best:
    #         print('\n')
    #         print(out)
    #         print('\n')
    #         best = out
    #         best_x = x.copy()
        
    # print(y)
    # print(min(y))
    # print(best_x)

    # # [X, F, flag, xkin] = pounders(obj_fun, X0, n, mpmax, nfmax, gtol, delta, nfs, m, F0, xind, Low, Upp, printf)
    [X, F, flag, xkin] = pounders(obj_fun, X0, n, mpmax, nfmax, gtol, delta, nfs, m, F0, xind, Low, Upp, printf)

    print(F)
    print(np.sum(F**2,axis=1))

    np.savez('theta2_run.npz',X=X,F=F,xkin=xkin)

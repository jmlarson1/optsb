from run_track import RunTRACK
import numpy as np

# import sys
# sys.path.insert(0, '/home/jlarson/research/pounder-base/')
# from pounders import *
from pounders import pounders

def obj_fun(x):
    print(x)
    rs = RunTRACK()
    run_dir = rs.set_dir()
    quad_vals = list(x.squeeze())
    print(quad_vals)
    rs.set_track(run_dir, quad_vals)
    rs.run_track(run_dir)
    df_beam, df_coord, df_step = rs.get_output(run_dir)
    x = df_coord["x[cm]"].to_numpy()
    y = df_coord["y[cm]"].to_numpy()
    out = np.hstack((x,y))
    return out

if __name__ == "__main__":
    # x = np.array([[1098.47, -1985.25, 1242.06]])
    x = np.array([[720.99624333, -1896.45344981,  1656.26142883]])
    y = obj_fun(x)
    print(np.sum(obj_fun(x)**2))

    n = 3
    X0 = x
    # mpmax [int] Maximum number of interpolation points (>n+1) (2*n+1)
    mpmax = 2 * n + 1
    # nfmax   [int] Maximum number of function evaluations (>n+1) (100)
    nfmax = 100
    # gtol [dbl] Tolerance for the 2-norm of the model gradient (1e-4)
    gtol = 10 ** -13
    # delta [dbl] Positive trust region radius (.1)
    delta = 0.1
    # nfs  [int] Number of function values (at X0) known in advance (0)
    nfs = 0
    # m [int] number of residuals
    m = 2002
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
    [X, F, flag, xkin] = pounders(obj_fun, X0, n, mpmax, nfmax, gtol, delta, nfs, m, F0, xind, Low, Upp, printf, 0, 2)

    print(F)
    print(np.sum(F**2,axis=1))

    np.savez('/home/jlarson/run2.npz',X=X,F=F,xkin=xkin)

% addpath('../../../poptus/IBCDFO/pounders/m'); % formquad, bmpts, boxline, phi2eval
% addpath('../../../poptus/IBCDFO/manifold_sampling/m/'); % For manifold_sampling_primal
% addpath('../../../poptus/IBCDFO/manifold_sampling/m/h_examples'); % For pw_maximum

addpath('/home/mmenickelly/IBCDFO/pounders/m'); % formquad, bmpts, boxline, phi2eval
addpath('/home/mmenickelly/IBCDFO/manifold_sampling/m/'); % For manifold_sampling_primal
addpath('/home/mmenickelly/IBCDFO/manifold_sampling/m/h_examples'); % For pw_maximum


global allX allF

nfmax = 600;

subprob_switch = 'linprog';
SolverNumber = 0;

n = 12;
m = 12;

LB = [-7500 0 -7500 0 -2500 0 -2500 -2500 0 0 -2500 0];
UB = [0 7500 0 2500 0 2500 0 0 2500 2500 0 2500];

x0 = [-5400.0, 4470.0, -3000.0, 875.0, -1150.0, 1077.0, -1130.0, -717.0, 535.0, 737.0, -1500.0, 856.0];

hfun = @pw_maximum;
Ffun = @call_track_sim_from_matlab;
allX = [];
allF = [];
[X, F, h, xkin, flag] = manifold_sampling_primal(hfun, Ffun, x0, LB, UB, nfmax, subprob_switch);
assert(flag >= 0, "Problem with manifold sampling");
SolverNumber = SolverNumber + 1;
Results{SolverNumber}.alg = 'Manifold sampling';
Results{SolverNumber}.problem = 'calem_prob';
Results{SolverNumber}.Fvec = F;
Results{SolverNumber}.H = h;
Results{SolverNumber}.X = X;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

allX = [];
allF = [];
composed = @(x) max(call_track_sim_from_matlab(x));
options = optimset('MaxFunEvals', nfmax/10);
[x, fval, exitflag, output] = fminsearchbnd(composed, x0, LB, UB, options);

for i = 1:size(allF, 1)
    h(i) = max(allF(i, :));
end
SolverNumber = SolverNumber + 1;
Results{SolverNumber}.alg = 'Nelder-Mead';
Results{SolverNumber}.problem = 'calem_prob';
Results{SolverNumber}.Fvec = allF;
Results{SolverNumber}.H = h;
Results{SolverNumber}.X = allX;
% %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

save(['Results_track_nfmax=' int2str(nfmax) '.mat'], 'Results', 'SolverNumber');

% npmax = 91;
% gtol = 1e-13;
% delta = 0.3;
% nfs = 0;
% F0 = [];
% xkin = 1;
% printf = 0;
% spsolver = 1;
%
% [X, F, flag, xkin] = pounders(Ffun, x0, n, npmax, nfmax, gtol, delta, nfs, m, F0, xkin, LB, UB, printf, spsolver);

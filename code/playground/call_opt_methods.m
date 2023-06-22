%addpath('/home/jmlarson/research/poptus/IBCDFO/pounders/m'); % formquad, bmpts, boxline, phi2eval
%addpath('/home/jmlarson/research/poptus/IBCDFO/manifold_sampling/m/'); % For manifold_sampling_primal
%addpath('/home/jmlarson/research/poptus/IBCDFO/manifold_sampling/m/h_examples'); % For pw_maximum

addpath('/home/mmenickelly/IBCDFO/pounders/m'); % formquad, bmpts, boxline, phi2eval
addpath('/home/mmenickelly/IBCDFO/manifold_sampling/m/'); % For manifold_sampling_primal
addpath('/home/mmenickelly/IBCDFO/manifold_sampling/m/h_examples'); % For pw_maximum


global allX allF

npat = 5000;
nfmax = 120;

subprob_switch = 'linprog';
SolverNumber = 0;

n = 3;
m = 12;

LB = [-4000 0 -4000];
UB = [0 4000 0];

x0 =  [-1432.311197351177, 1813.4027595220934, -966.9415661755137];
% x0 = [952.496159375000e+000   -1.94223604077761e+003    1.00694574562500e+003    907.724217587984e+000   -774.585299624646e+000   -431.684081111314e+000    483.238434348558e+000   -309.859770262683e+000    116.529810344415e+000   -218.918065625000e+000    592.752634852370e+000   -158.250727314826e+000]

for npat = 5000 %[5000 10000 15000 20000 25000 30000]
    system(['bash adjust_npat.sh ' num2str(npat)]);
    %x0 = LB + (UB - LB)/2.0;
    hfun = @pw_maximum;
    % Ffun = @(x)call_several_track_sim_from_matlab(x,[1,4,7],npat);
    ub = [1.0, 1.0, 0.24, 1.0, 0.99, 0.21, 1.0, 1.0, 0.38, 1.0, 0.31, 0.46]
    Ffun = @(x)known_upper_bounds_on_trans(x, 1:m, ub, npat)
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
    x0 = X(xkin,:);
end

% allX = [];
% allF = [];
% composed = @(x) max(call_track_sim_from_matlab(x));
% options = optimset('MaxFunEvals', nfmax/10);
% [x, fval, exitflag, output] = fminsearchbnd(composed, x0, LB, UB, options);

% for i = 1:size(allF, 1)
%     h(i) = max(allF(i, :));
% end
% SolverNumber = SolverNumber + 1;
% Results{SolverNumber}.alg = 'Nelder-Mead';
% Results{SolverNumber}.problem = 'calem_prob';
% Results{SolverNumber}.Fvec = allF;
% Results{SolverNumber}.H = h;
% Results{SolverNumber}.X = allX;
% % %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

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

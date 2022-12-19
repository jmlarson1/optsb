R = load("Results_track_nfmax=20.mat");

R = R(1);
Results = R.Results;
num = R.SolverNumber;

solver_names = {};
hold off
for i = 1:num
    l = length(Results{i}.H);
    scatter(1:l, Results{i}.H, 'filled');
    hold on;
    solver_names{i} = Results{i}.alg;
end

legend(solver_names)
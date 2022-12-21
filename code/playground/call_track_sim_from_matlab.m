function F = call_track_sim_from_matlab(x)
global allX allF
x = x(:)';

str = ['python3 loop_over_theta.py ', num2str(x, '%16.16f ')];
disp(str)
system(str);    
F = load('fvec.out')';
system('rm fvec.out');
assert(all(size(F) == [1 12]), "F is not the correct size")

if isempty(allX)
    allX = x;
    allF = F;
else
    allX = [allX; x];
    allF = [allF; F];
end

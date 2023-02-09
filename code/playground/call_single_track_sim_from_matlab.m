function F = call_single_track_sim_from_matlab(x,i)
global allX allF
x = x(:)';

str = ['python3 single_theta.py ', num2str(x, '%16.16f '), ' ', num2str(i, '%d ')];
disp(str);
system(str);
F = -1.0*load('fvec.out')'
system('rm fvec.out');
%assert(all(size(F) == [1 12]), "F is not the correct size");

if isempty(allX)
    allX = x;
    allF = F;
else
    allX = [allX; x];
    allF = [allF; F];
end

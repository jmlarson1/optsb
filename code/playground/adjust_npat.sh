# Do a git reset on .dat file
git checkout ../track/transport_line/theta_*/track.dat
# Replace the npat=100k with npat=$1 (the first argument to this script)
sed -i -e "s/npat=100000,100000,100000/npat=${1},${1},${1}/g" ../track/transport_line/theta_*/track.dat
sed -i -e "s/npat=100000/npat=${1}/g" ../track/transport_line/theta_*/track.dat

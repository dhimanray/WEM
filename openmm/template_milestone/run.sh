#!/bin/bash


#equilibrate
cd equilibration
python equilibration.py
cd ..

# Make sure environment is set
source env.sh


# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs istates west.h5
mkdir   seg_logs traj_segs istates

#copy files to bstate directory for starting points
cp equilibration/distance.dat bstates/dist.dat
cp equilibration/equilibration.xml bstates/bstate.xml

cp common_files/prod.py bstates/prod_unrestrain.py
cp common_files/prod_restrain.py bstates/prod.py

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"
#TSTATE_ARGS="--tstate-file $WEST_SIM_ROOT/tstate.file"

# Run w_init
$WEST_ROOT/bin/w_init $BSTATE_ARGS  $TSTATE_ARGS  --segs-per-state XX  --work-manager=threads "$@"


# Clean up
rm -f west.log west-restrain.log

# Run restrained dynamics
$WEST_ROOT/bin/w_run -r west-restrain.cfg --work-manager processes --n-workers 4 "$@" &> west-restrain.log

cd bstates
mv prod.py prod_restrain.py
mv prod_unrestrain.py prod.py
cd ..

# Run unrestrained dynamics
$WEST_ROOT/bin/w_run -r west.cfg --work-manager processes --n-workers 4 "$@" &> west.log


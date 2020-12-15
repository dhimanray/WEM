#!/bin/bash


#equilibrate
cd equilibration
/home/dhiman/NAMD_2.13_Linux-x86_64-multicore/namd2 equilibration.conf > equilibration.log
#*** Make sure to provide the correct path to NAMD in your cluster in above line ***#

python calc_rxn_coor.py > distance.dat
cd ..

# Make sure environment is set
source env.sh


# Clean up from previous/ failed runs
rm -rf traj_segs seg_logs istates west.h5
mkdir   seg_logs traj_segs istates

#copy files to bstate directory for starting points
cp equilibration/distance.dat bstates/dist.dat
cp equilibration/milestone_equilibration.restart.coor bstates/seg.coor
cp equilibration/milestone_equilibration.colvars.traj  bstates/seg.colvars.traj
cp equilibration/milestone_equilibration.restart.vel  bstates/seg.vel
cp equilibration/milestone_equilibration.restart.xsc  bstates/seg.xsc
cp common_files/colvars.in bstates/colvars_unrestrain.in
cp common_files/colvars_restrain.in bstates/colvars.in

# Set pointer to bstate and tstate
BSTATE_ARGS="--bstate-file $WEST_SIM_ROOT/bstates/bstates.txt"
#TSTATE_ARGS="--tstate-file $WEST_SIM_ROOT/tstate.file"

# Run w_init
$WEST_ROOT/bin/w_init $BSTATE_ARGS  $TSTATE_ARGS  --segs-per-state SEGS_PER_STATE  --work-manager=threads "$@"


# Clean up
rm -f west.log west-restrain.log

# Run restrained dynamics
$WEST_ROOT/bin/w_run -r west-restrain.cfg --work-manager processes --n-workers 4 "$@" &> west-restrain.log

cd bstates
mv colvars.in colvars_restrain.in
mv colvars_unrestrain.in colvars.in
cd ..

# Run unrestrained dynamics
$WEST_ROOT/bin/w_run -r west.cfg --work-manager processes --n-workers 4 "$@" &> west.log


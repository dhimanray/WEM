#!/bin/bash

if [ -n "$SEG_DEBUG" ] ; then
  set -x
  env | sort
fi

cd $WEST_SIM_ROOT
mkdir -pv $WEST_CURRENT_SEG_DATA_REF
cd $WEST_CURRENT_SEG_DATA_REF

ln -sv $WEST_SIM_ROOT/common_files/bstate.pdb .
#ln -sv $WEST_SIM_ROOT/common_files/DistanceReporter.py .
#ln -sv $WEST_PARENT_DATA_REF/dist.dat ./parent.dat

if [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_CONTINUES" ]; then
  ln -sv $WEST_PARENT_DATA_REF/seg.xml ./parent.xml
  ln -sv $WEST_PARENT_DATA_REF/dist.dat ./parent.dat
elif [ "$WEST_CURRENT_SEG_INITPOINT_TYPE" = "SEG_INITPOINT_NEWTRAJ" ]; then
  ln -sv $WEST_PARENT_DATA_REF ./parent.xml
  ln -sv $WEST_SIM_ROOT/bstates/dist.dat ./parent.dat
fi


# Run the dynamics with OpenMM
python $WEST_SIM_ROOT/bstates/nacl_prod.py

echo "$(pwd)"
#Calculate pcoord with MDAnalysis
#python $WEST_SIM_ROOT/common_files/get_distance.py
python $WEST_SIM_ROOT/westpa_scripts/convert.py > dist.dat
cat dist.dat > $WEST_PCOORD_RETURN

# Clean up
mkdir save
mv seg.xml save/
mv dist.dat save/
mv distance.dat save/
mv seg.dcd save/

rm *

mv save/* .

rm -r save

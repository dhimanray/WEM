#!/bin/bash
set -x
cd $WEST_SIM_ROOT/bstates || exit 1
cat distance.dat | tail -n 1 > $WEST_PCOORD_RETURN

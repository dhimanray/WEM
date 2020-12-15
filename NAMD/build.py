#!/usr/bin/env python

import numpy as np
import os
import subprocess

#define milestone positions
#milestones = np.arange(2.0,5.0,1.0)
#can also be done manually
milestones = [2.,2.6,3.0,4.0]

#define weighted ensemble bin width
#**bin edges are automatically placed at the milestone positions**#
we_bin_width = 0.2

#harmonic restrain for equilibration
k_eq = 40.0

#harmonic restrain for WEM
k_res = 40.0

#steps of simulation
minimization_nsteps = 1000
equilibration_nsteps = 5000
equilibration_dcd_frequency = 1000
#restrained_nsteps = 100
nsteps = 100
print_frequency = 10
dcd_frequency = 100

#cfg file parameters
pcoord_len = nsteps/print_frequency + 1
n_traj_per_bin = 5
n_iterations_restrained = 2
n_iterations = 10



def generate_we_bins(milestones,milestone_index,bin_width):
    '''Generate the positions of the weighted ensemble bin edges
    around a given milestone

    milestones: Array of milestone positions

    milestone_index: Zero based ndex of the current milestone

    bin_width: width of weighted ensemble bin'''

    if milestone_index == 0:
        start = milestones[milestone_index]
        end = milestones[milestone_index+1]
        current = start
    elif milestone_index == len(milestones)-1:
        start = milestones[milestone_index-1]
        end = milestones[milestone_index]
        current = end
    else :
        start = milestones[milestone_index-1]
        end = milestones[milestone_index+1]
        current = milestones[milestone_index]

    if int((end - current)%bin_width) != 0:
        print("Milestone spacing must be integer multiple of bin width \n Error in milestone: %d"%milestone_index)
        return
    elif int((current - start)%bin_width) != 0:
        print("Milestone spacing must be integer multiple of bin width \n Error in milestone: %d"%milestone_index)
        return

    numbins = int((end - start)/bin_width)
    bin_list = [start + bin_width*i for i in range(numbins+1) ]

    #a = np.arange(start,current,bin_width)
    #b = np.arange(current,end+bin_width,bin_width)

    #print(np.concatenate((a,b)))
    #bins = np.concatenate((a,b)).tolist()

    bin_list = [round(num, 2) for num in bin_list]
    bin_list.append('inf')
    bin_list.insert(0,'-inf')

    return bin_list

#x = generate_we_bins(milestones,2,we_bin_width)
#print(str(x))

boundaries = str(['-inf',milestones[0],milestones[len(milestones)-1],'inf'])
bound = str([milestones[0]])
unbound = str([milestones[len(milestones)-1]])




current = os.getcwd()

#print(current)

for i in range(len(milestones)):

    #define the directory name for milestones
    dir_name = 'milestone_%d'%i

    #create directory
    #path = os.path.join(current,dir_name)
    #os.mkdir(path)

    #remove old milestones
    os.system('rm -r %s'%dir_name)

    #copy the template files into each directory
    os.system('cp -r template_milestone %s'%dir_name)

    #copy structure files to equilibration directory
    os.system('cp structure_files/topology.psf %s/equilibration/'%dir_name)
    os.system('cp structure_files/milestone_%d.pdb %s/equilibration/structure.pdb'%(i,dir_name))
    os.system('cp structure_files/equilibration.conf %s/equilibration/equilibration.conf'%dir_name)
    os.system('cat structure_files/colvars.in %s/equilibration/restrain.in > %s/equilibration/colvars.in'%(dir_name,dir_name))

    #copy structure files to common files directory
    os.system('cp structure_files/topology.psf %s/common_files/'%dir_name)
    os.system('cp structure_files/milestone_%d.pdb %s/common_files/structure.pdb'%(i,dir_name))
    os.system('cp structure_files/colvars.in %s/common_files/'%dir_name)
    os.system('cp structure_files/md.conf %s/common_files/md.conf'%dir_name)
    os.system('cat structure_files/colvars.in %s/common_files/restrain.in > %s/common_files/colvars_restrain.in'%(dir_name,dir_name))


    #make modifications inside each milestone directory

    #change the equilibration files
    subprocess.call(["sed -i 's/K_EQ/%0.2f/g' %s/equilibration/colvars.in"%(k_eq,dir_name)], shell=True)
    subprocess.call(["sed -i 's/X_0/%0.2f/g' %s/equilibration/colvars.in"%(milestones[i],dir_name)], shell=True)
    subprocess.call(["sed -i 's/EQBM_TIME/%d/g' %s/equilibration/colvars.in"%(equilibration_nsteps,dir_name)], shell=True)
    subprocess.call(["sed -i 's/DCD_FREQUENCY/%d/g' %s/equilibration/equilibration.conf"%(equilibration_dcd_frequency,dir_name)], shell=True)
    subprocess.call(["sed -i 's/MINIMIZATION_STEPS/%d/g' %s/equilibration/equilibration.conf"%(minimization_nsteps,dir_name)], shell=True)
    subprocess.call(["sed -i 's/EQUILIBRATION_STEPS/%d/g' %s/equilibration/equilibration.conf"%(equilibration_nsteps,dir_name)], shell=True)
    subprocess.call(["sed -i 's/TRAJ_FREQ/%d/g' %s/equilibration/colvars.in"%(print_frequency,dir_name)], shell=True)

    #change the colvars file for restrained dynamics 
    subprocess.call(["sed -i 's/K_RES/%0.2f/g' %s/common_files/colvars_restrain.in"%(k_res,dir_name)], shell=True)
    subprocess.call(["sed -i 's/X_0/%0.2f/g' %s/common_files/colvars_restrain.in"%(milestones[i],dir_name)], shell=True)
    subprocess.call(["sed -i 's/TRAJ_FREQ/%d/g' %s/common_files/colvars_restrain.in"%(print_frequency,dir_name)], shell=True)

    #change the colvars file for regular dynamics
    subprocess.call(["sed -i 's/TRAJ_FREQ/%d/g' %s/common_files/colvars.in"%(print_frequency,dir_name)], shell=True)

    #change the configuration file
    subprocess.call(["sed -i 's/DCD_FREQUENCY/%d/g' %s/common_files/md.conf"%(dcd_frequency,dir_name)], shell=True)
    subprocess.call(["sed -i 's/NUM_STEPS/%d/g' %s/common_files/md.conf"%(nsteps,dir_name)], shell=True)
    
    #change west-restrain.cfg
    subprocess.call(["sed -i 's/PCOORD_LEN/%d/g' %s/west-restrain.cfg"%(pcoord_len,dir_name)], shell=True)
    subprocess.call(["sed -i 's/BIN_TARGET_COUNTS/%d/g' %s/west-restrain.cfg"%(n_traj_per_bin,dir_name)], shell=True)
    subprocess.call(["sed -i 's/MAX_TOTAL_ITERATIONS/%d/g' %s/west-restrain.cfg"%(n_iterations_restrained,dir_name)], shell=True)
    #Add bins and boundaries etc.
    subprocess.call(["sed -i 's/This part will be replaced by the weighted ensemble bin edges/%s/g' %s/west-restrain.cfg"%(str(generate_we_bins(milestones,i,we_bin_width)),dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-boundaries/%s/g' %s/west-restrain.cfg"%(boundaries,dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-bound/%s/g' %s/west-restrain.cfg"%(bound,dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-unbound/%s/g' %s/west-restrain.cfg"%(unbound,dir_name)], shell=True)



    #change west.cfg
    subprocess.call(["sed -i 's/PCOORD_LEN/%d/g' %s/west.cfg"%(pcoord_len,dir_name)], shell=True)
    subprocess.call(["sed -i 's/BIN_TARGET_COUNTS/%d/g' %s/west.cfg"%(n_traj_per_bin,dir_name)], shell=True)
    subprocess.call(["sed -i 's/MAX_TOTAL_ITERATIONS/%d/g' %s/west.cfg"%(n_iterations,dir_name)], shell=True)
    #Add bins and boundaries etc.
    subprocess.call(["sed -i 's/This part will be replaced by the weighted ensemble bin edges/%s/g' %s/west.cfg"%(str(generate_we_bins(milestones,i,we_bin_width)),dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-boundaries/%s/g' %s/west.cfg"%(boundaries,dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-bound/%s/g' %s/west.cfg"%(bound,dir_name)], shell=True)
    subprocess.call(["sed -i 's/script-unbound/%s/g' %s/west.cfg"%(unbound,dir_name)], shell=True)

    #change westpa-scripts directory
    #change milestone_calculation (convert.py)
    if i == 0:
        os.system('cp %s/westpa_scripts/convert_first_milestone.py %s/westpa_scripts/convert.py'%(dir_name,dir_name))
        subprocess.call(["sed -i 's/ENDPOINT/%0.2f/g' %s/westpa_scripts/convert.py"%(milestones[i+1],dir_name)], shell=True)
    elif i == len(milestones)-1:
        os.system('cp %s/westpa_scripts/convert_last_milestone.py %s/westpa_scripts/convert.py'%(dir_name,dir_name))
        subprocess.call(["sed -i 's/ENDPOINT/%0.2f/g' %s/westpa_scripts/convert.py"%(milestones[i-1],dir_name)], shell=True)
    else :
        subprocess.call(["sed -i 's/ENDPOINT_1/%0.2f/g' %s/westpa_scripts/convert.py"%(milestones[i-1],dir_name)], shell=True)
        subprocess.call(["sed -i 's/ENDPOINT_2/%0.2f/g' %s/westpa_scripts/convert.py"%(milestones[i+1],dir_name)], shell=True)

    #change run.sh
    subprocess.call(["sed -i 's/SEGS_PER_STATE/%d/g' %s/run.sh"%(n_traj_per_bin,dir_name)], shell=True)

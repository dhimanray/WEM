from simtk.openmm.app import *
from simtk.openmm import *
from simtk.unit import *
from sys import stdout
import sys
import numpy as np

#==================== CREATE SYSTEM =======================================================#
pdb = PDBFile('bstate.pdb')
forcefield = ForceField('amber14-all.xml', 'amber14/tip3p.xml')

system = forcefield.createSystem(pdb.topology, nonbondedMethod=PME, nonbondedCutoff=1*nanometer,
                             constraints=HBonds)
for force in system.getForces():
        force.setForceGroup(10)


#choose particle groups. Reaction coordinate is the distance between the groups.
particles1 = [2,3,4]
particles2 = [5,6,7]


#================= Add harmonic force to center of mass distance collective variable (RESTRAINT RELEASE)=============#
#k = 10.0 * kilocalories_per_mole / angstroms**2
#particles1 = [0,2,3]
#particles2 = [1,4,5]
#dist_force = CustomCentroidBondForce(2, "0.5*k*(distance(g1,g2)-4.0)^2")
#dist_force.addPerBondParameter("k")
#dist_force.addGroup(particles1)
#dist_force.addGroup(particles2)
#dist_force.addBond([0,1],[k])
#dist_force.setForceGroup(1)
#system.addForce(dist_force)



#================== Define reporter for the collective variable =========================================#

#Function to save the value of collective variable (distance)
class ColvarReporter1(object):
    def __init__(self, file, reportInterval):
        self._out = open(file, 'w')
        self._reportInterval = reportInterval

    def __del__(self):
        self._out.close()

    def describeNextReport(self, simulation):
        steps = self._reportInterval - simulation.currentStep%self._reportInterval
        return (steps, True, False, False, False) # return (steps, positions, velocities, forces, energies)

    def report(self, simulation, state):
        state = simulation.context.getState(getPositions = True, getVelocities = False, getForces = False, getEnergy = False, getParameters = False, enforcePeriodicBox = False, groups = {0}) #each number after "b" is a group (from right to left) (in total there are 32 groups).
		  	                                             #The last number is the group "0", i.e. unperturbed,
		  	                                             #the second last is the group "1", i.e. the perturbation of phi.
		  	                                             #the third last  is the group "2", i.e. the perturbation of psi.
		  	                                             #If all are 1, you get the energy of the full system
        r1 = state.getPositions(asNumpy=True)[particles1]
        m1 = [system.getParticleMass(particles1[i]) for i in range(len(particles1))]
        r1com = np.average(r1,axis=0,weights=m1)

        r2 = state.getPositions(asNumpy=True)[particles2]
        m2 = [system.getParticleMass(particles2[i]) for i in range(len(particles2))]
        r2com = np.average(r2,axis=0,weights=m2)

        dist = np.linalg.norm(r2com - r1com) * 10.0 #convert nm to Angstrom
        print(dist,file=self._out) 


#=================== Specify other simulation detailes (temperature, pressure etc) ====================#

system.addForce(MonteCarloBarostat(1*bar, 300*kelvin))
integrator = LangevinIntegrator(300*kelvin, 1/picosecond, 0.001*picoseconds)

simulation = Simulation(pdb.topology, system, integrator)
simulation.context.setPositions(pdb.positions)

simulation.loadState('parent.xml')

#=================== Add reporters to print output =====================================================#

simulation.reporters.append(StateDataReporter('seg.log', 100, step=True, potentialEnergy=True, kineticEnergy=True, temperature=True))
dcdfilename = 'seg.dcd'
simulation.reporters.append(DCDReporter(dcdfilename, XX))

outfilename = "distance.dat"
simulation.reporters.append(ColvarReporter1(outfilename,XX)) #MODIFIED BY SCRIPT

#=================== RUN SIMULATION ====================================================================#
simulation.step(XX)
simulation.saveState('seg.xml')



"""
DistanceReporter.py:
Authors: Dhiman Ray
Modified from
----------------------------------------------------------------------
DistanceReporter.py: 
Authors: Yuan-Yu
Contributors: Justin

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS, CONTRIBUTORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
USE OR OTHER DEALINGS IN THE SOFTWARE.
------------------------------------------------------------------------
"""
__author__ = "Dhiman Ray"
__version__ = "0.1"

import numpy as np

class DistanceReporter(object):
    """DistanceReporter outputs the distance between two atoms or atom groups to a CSV file

    To use it, create a DistanceReporter, then add it to the Simulation's list of reporters.
    """

    def __init__(self, file, reportInterval, group1_atom_indices=[], group2_atom_indices=[], report_step=False):
        """Create a DistanceReporter.

        Parameters
        ----------
        file : string
            The file to write to
        reportInterval : int
            The interval (in time steps) at which to write frames
        group1_atom_indices : List=[]
            The atom indices in group1
        group2_atom_indices : List=[]
            The atom indices in group2
        report_step: bool
            Reports the current step number in the output file
        """
        self._reportInterval = reportInterval
        #self._forceGroup = forceGroup if forceGroup else -1
        self._group1_atom_indices = group1_atom_indices
        self._group2_atom_indices = group2_atom_indices
        #self._force_constant = force_constant
        self._report_step = report_step
        self._out = open(file, 'w')
        self._count = 0
        self._maxFlushCycle = 10
        self._text = ''

    def describeNextReport(self, simulation):
        """Get information about the next report this object will generate.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for

        Returns
        -------
        tuple
            A five element tuple. The first element is the number of steps
            until the next report. The remaining elements specify whether
            that report will require positions, velocities, forces, and
            energies respectively.
        """         
        steps = self._reportInterval - simulation.currentStep%self._reportInterval
        return (steps, True, False, False, False)

    def report(self, simulation, state):
        """Generate a report.

        Parameters
        ----------
        simulation : Simulation
            The Simulation to generate a report for
        state : State
            The current state of the simulation
        """
        group1_coords = state.getPositions(asNumpy=True)[self._group1_atom_indices]
        group2_coords = state.getPositions(asNumpy=True)[self._group2_atom_indices]

        if len(self._group1_atom_indices) > 1:
            group1_coords = np.mean(group1_coords)
        if len(self._group2_atom_indices) > 1:
            group2_coords = np.mean(group2_coords)

        distance = np.linalg.norm(group1_coords - group2_coords)
        '''
        #vec_diff[2,:] *= -1

        #first_plane_norm = np.cross(vec_diff[0], vec_diff[1])
        first_plane_norm /= np.linalg.norm(first_plane_norm)
        3second_plane_norm = np.cross(vec_diff[2], vec_diff[1])
        second_plane_norm /= np.linalg.norm(second_plane_norm)

        dihedral_cos = first_plane_norm.dot(second_plane_norm)

        plane_cross = np.cross(second_plane_norm, first_plane_norm)
        dihedral_sin = np.sign(plane_cross.dot(vec_diff[1,:])) * np.linalg.norm(plane_cross)

        dihedral_angle_rad = np.arctan2(dihedral_sin, dihedral_cos)
        dihedral_angle_deg = np.rad2deg(dihedral_angle_rad)

        force = -0.5 * self._force_constant * np.sin(dihedral_angle_rad - simulation.context.getParameter('theta0'))
        '''
        #if self._report_step:
        #    self._text += '{:d},{:f},{:f},{:f}\n'.format(simulation.currentStep, dihedral_angle_deg, np.rad2deg(simulation.context.getParameter('theta0')), force)

        #else:
        self._text += '{:f}\n'.format(distance)

    def write_to_file(self):
        self._out.write(self._text)
        self._out.flush()
        self._text = ''

    def __del__(self):
        self._out.write(self._text)
        self._out.close()

import rps.robotarium as robotarium
from PiOSFacility import PiOSFacility
from rps.utilities.transformations import *
from rps.utilities.barrier_certificates import *
from rps.utilities.misc import *
from rps.utilities.controllers import *
from get_init import *
import numpy as np
import time
# Instantiate Robotarium object
init = get()
N, initial_conditions = init.get_init_pose()
# r = robotarium.Robotarium(number_of_robots=N, show_figure=True, initial_conditions=initial_conditions, sim_in_real_time=False)
r = PiOSFacility(number_of_robots=N, show_figure=True, initial_conditions=initial_conditions, sim_in_real_time=False)
# Define goal points by removing orientation from poses
goal_points = np.array([
    [1.0],
    [0.4],
    [3.14]
])
# Create single integrator position controller
single_integrator_position_controller = create_si_position_controller()
# Create barrier certificates to avoid collision
# si_barrier_cert = create_single_integrator_barrier_certificate()
si_barrier_cert = create_single_integrator_barrier_certificate_with_boundary()

_, uni_to_si_states = create_si_to_uni_mapping()

# Create mapping from single integrator velocity commands to unicycle velocity commands
si_to_uni_dyn = create_si_to_uni_dynamics_with_backwards_motion(angular_velocity_limit=0.8)
# define x initially
x = r.get_poses()
x_si = uni_to_si_states(x)
r.step_real()
r.get_real_position()

# While the number of robots at the required poses is less
# than N...
while np.size(at_pose(np.vstack((x_si, x[2, :])), goal_points, rotation_error=100)) != N:
    # Get poses of agents
    x = r.get_poses()
    x_si = uni_to_si_states(x)

    # Create single-integrator control inputs
    dxi = single_integrator_position_controller(x_si, goal_points[:2][:])

    # Create safe control inputs (i.e., no collisions)
    dxi = si_barrier_cert(dxi, x_si)

    # Transform single integrator velocity commands to unicycle
    dxu = si_to_uni_dyn(dxi, x)

    # Set the velocities by mapping the single-integrator inputs to unciycle inputs
    r.set_velocities(np.arange(N), dxu)
    # Iterate the simulation
    r.step_real()
    time.sleep(0.033)
    r.get_real_position()
    print(x)

# Call at end of script to print debug information and for your script to run on the Robotarium server properly
for i in range(50):
    r.stop()
    time.sleep(0.033)
    print(i)
print('ok')
r.call_at_scripts_end()
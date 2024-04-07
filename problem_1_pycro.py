import pycro
import utils
from pycromanager import Acquisition, multi_d_acquisition_events


#user parameters
save_dir = r"C:/cz/problem_1"
channels = ["DAPI", "FITC"]
z_slices = 12
step_size = 0.1
z_start = 0
#set to 1 for positive and -1 for negative
z_stack_direction = 1


#other acquisition parameters
#for some reason, this takes (z_slices - 1) takes 13 slices, so -2 instead
z_end = z_start + z_stack_direction*(z_slices - 2)*step_size
xy_positions = utils.get_stage_grid_positions()


with Acquisition(save_dir, "acquisition") as acq:
    events = multi_d_acquisition_events(z_start=z_start,
                                        z_end=z_end,
                                        z_step=step_size,
                                        channel_group=pycro.CHANNEL,
                                        channels=channels,
                                        xy_positions=xy_positions)
    acq.acquire(events)
    
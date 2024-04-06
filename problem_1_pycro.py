import pycro
import utils
from pycromanager import Acquisition, multi_d_acquisition_events


save_dir = r"C:/cz/problem_1"
channels = ["DAPI", "FITC"]
z_slices = 12
z_start = 0
z_end = 1.1
step_size = abs(z_start-z_end)/z_slices
xy_positions = utils.get_stage_grid_positions()
#the more typical acquisition order for large grids
order = "tpzc"


with Acquisition(save_dir, "acquisition") as acq:
    events = multi_d_acquisition_events(z_start=z_start,
                                        z_end=z_end,
                                        z_step=step_size,
                                        channel_group=pycro.CHANNEL,
                                        channels=channels,
                                        xy_positions=xy_positions,
                                        order="tpzc")
    acq.acquire(events)
    
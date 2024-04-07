"""
Problem 1 using MDA to perform acquistition.
"""
import pycro
import utils
from pycro import studio

#user parameters
save_dir = r"C:/cz/problem_1"
channels = ["DAPI", "FITC"]
z_slices = 12
step_size = 0.1
z_start = 0
#set to 1 for positive and -1 for negative
z_stack_direction = 1

#other acquisition parameters
z_end = z_start + z_stack_direction*(z_slices - 1)*step_size
xy_positions = utils.get_stage_grid_positions()
xyz_positions = [(xy[0], xy[1], z_start) for xy in xy_positions]

#set position list in MM to position list with positions from xyz_positions
pycro.set_position_list(xyz_positions)

seq_builder = studio.acquisitions().sequence_settings_builder()
seq_builder = seq_builder \
                  .channel_group(pycro.CHANNEL) \
                  .channels(pycro.get_channel_spec_list(channels)) \
                  .prefix("pos") \
                  .save(True) \
                  .root(save_dir) \
                  .save_mode(pycro.MULTIPAGE_TIFF) \
                  .slice_z_bottom_um(z_start) \
                  .slice_z_top_um(z_end) \
                  .slice_z_step_um(step_size) \
                  .use_channels(True) \
                  .use_position_list(True) \
                  .use_slices(True)
seq_settings = seq_builder.build()
studio.acquisitions().run_acquisition_with_settings(seq_settings, True)

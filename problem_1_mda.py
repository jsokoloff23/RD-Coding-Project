import pycro
import utils
from pycro import studio


save_dir = r"C:/cz/problem_1"
channels = ["DAPI", "FITC"]
z_slices = 12
z_start = 0
z_end = 1.1
step_size = abs(z_start-z_end)/z_slices
xy_positions = utils.get_stage_grid_positions()
xyz_positions = [(xy[0], xy[1], z_start) for xy in xy_positions]
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

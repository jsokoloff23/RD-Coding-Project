import pycro
import utils
from pycro import core


save_dir = r"C:/cz/problem_1"
channels = ["DAPI", "FITC"]
z_slices = 12
z_start = 0
z_end = 1.1
step_size = abs(z_start-z_end)/z_slices
xy_positions = utils.get_stage_grid_positions()


for pos_num, pos in enumerate(xy_positions):
    x_pos = pos[0]
    y_pos = pos[1]
    #new datastore and metadta for each position to be consistent with
    #MM's convention of doing so.
    data = pycro.MultipageDatastore(f"{save_dir}/pos_{pos_num}")
    summary = pycro.SummaryMetadataBuilder().channel_list(
        channels).z(z_slices).step(step_size).build()
    data.set_summary_metadata(summary)
    core.set_xy_position(x_pos, y_pos)
    for z in range(z_slices):
        #determine which direction stage is moving
        if z_start <= z_end:
            z_pos = z_start + z*step_size
        else:
            z_pos = z_start - z*step_size
        core.set_position(z_pos)
        for channel_num, channel in enumerate(channels):
            pycro.set_channel(channel)
            image = pycro.snap_image()
            coords = pycro.ImageCoordsBuilder().z(z).c(channel_num).build()
            meta = pycro.ImageMetadataBuilder(image).x(x_pos).y(y_pos).z(z_pos).build()
            image = image.copy_with(coords, meta)
            try:
                data.put_image(image)
            except:
                pass
    data.close()

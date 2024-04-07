"""
Problem 1 using core as backend. In my lab, the acquisition code is 
written in this style, mainly because we require the use of other external 
hardware devices and this scripting style allows for finer control of timing 
and hardware.
"""
import contextlib

import pycro
import utils
from pycro import core

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

for pos_num, pos in enumerate(xy_positions):
    x_pos = pos[0]
    y_pos = pos[1]
    #new datastore and metadta for each position to be consistent with
    #MM's convention of doing so.
    data = pycro.MultipageDatastore(f"{save_dir}/pos_{pos_num}")
    summary = pycro.SummaryMetadataBuilder().channel_list(
        channels).z(z_slices).step(step_size).build()
    data.set_summary_metadata(summary)
    #in our software, stage has its own module and set of api, so doesn't
    #violate abstraction layer principles.
    core.set_xy_position(x_pos, y_pos)
    for z in range(z_slices):
        #z position depends on which direction stage is moving
        z_pos = z_start + z*z_stack_direction*step_size
        core.set_position(z_pos)
        for channel_num, channel in enumerate(channels):
            pycro.set_channel(channel)
            image = pycro.snap_image()
            coords = pycro.ImageCoordsBuilder().z(z).c(channel_num).build()
            meta = pycro.ImageMetadataBuilder(image).x(x_pos).y(y_pos).z(z_pos).build()
            image = image.copy_with(coords, meta)
            #supress NullPointerException on Java side. 
            with contextlib.suppress(Exception):
                data.put_image(image)
    data.close()

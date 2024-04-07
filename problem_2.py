import numpy as np
from pycromanager import Acquisition, multi_d_acquisition_events

import pycro
from pycro import core


#user parameters
save_dir = r"problem_2_output"
channels = ["DAPI"]
exposure = 10
num_time_points = 100
pixel_value_target = 700
radius = 15


def image_process_fn(image, metadata):
    #creates array of pixels coords where pixel value is equal to target value
    pixel_coords = np.argwhere(image == pixel_value_target)
    for coord in pixel_coords:
        #coords are (y,x) because ndarray
        y, x = coord
        #grid to create mask
        y_range, x_range = np.ogrid[:image.shape[0], :image.shape[1]]
        #binary mask for pixels within radius of target pixel
        mask = (x_range - x)**2 + (y_range - y)**2 <= radius**2
        #sets pixels in image to black according to binary mask
        image[mask] = 0
        #set target pixel back to target value.
        image[y][x] = pixel_value_target
    return image, metadata


mode_prop = core.get_property(core.get_camera_device(), "Mode")
core.set_exposure(exposure)
core.set_property(core.get_camera_device(), "Mode", "Noise")
with Acquisition(save_dir, 
                 name="problem 2",
                 image_process_fn=image_process_fn) as acq:
    events = multi_d_acquisition_events(num_time_points=num_time_points,
                                        channel_group=pycro.CHANNEL,
                                        channels=channels)
    acq.acquire(events)
core.set_property(core.get_camera_device(), "Mode", mode_prop)

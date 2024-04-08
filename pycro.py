"""
This module is an adaptation of a module in the pycro-manager-based 
acquisition program I wrote for my lab, LS_Pycro_App. It holds the studio
and core objects, some useful constants, and some classes and functions that
help abstract the studio and core API. 

"""
import contextlib
from datetime import datetime

import pycromanager
from pycromanager import Studio, Core, JavaObject

studio = Studio()
core = Core()

#Public constants
CHANNEL = "Channel"
MULTIPAGE_TIFF = studio.data().get_preferred_save_mode().MULTIPAGE_TIFF


#private constants
#These are found in the MM summary metadata class and are used in setting the
#axis order in summary metadata.
_C_AXIS = "channel"
_T_AXIS = "time"
_Z_AXIS = "z"
_P_AXIS= "position"


class ImageCoordsBuilder():
    """
    Python wrapper of the coords builder class in Micro-Manager (see 
    DefaultCoordsBuilder). Contains only the coords necessary to have same 
    metadata format as MM Acquisitions (channel, z, time, and position).

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Coords.Builder.html

    ## Methods:

    every method returns self (akin the builder design), except for build() which returns an
    MM DefaultCoords object.

    #### c(channel_num:int)
        sets channel number

    #### z(z_num:int)
        sets z slice number

    #### t(time_num:int)
        sets time number

    #### build()
        returns MM DefaultCoords object
    """
    
    def __init__(self):
        self._coords_builder = studio.data().coords_builder()

    def c(self, num_c):
        self._coords_builder.c(num_c)
        return self

    def z(self, num_z):
        self._coords_builder.z(num_z)
        return self
    
    def t(self, num_t):
        self._coords_builder.t(num_t)
        return self

    #p (position) is pretty much only added to be used in summary metadata. 
    def p(self, num_p):
        self._coords_builder.p(num_p)
        return self

    def build(self):
        return self._coords_builder.build()


class SummaryMetadataBuilder():
    """
    Python wrapper of the summary metadata builder class in Micro-Manager 
    (see DefaultSummaryMetadataBuilder). Contains only the coords necessary to 
    have acceptable metadata (channel, z, and time).

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/SummaryMetadata.Builder.html

    The axis order is determined on the order of the called methods. That is, 
    if channel_list(), then z(), then t() are called, then the axis order will 
    be channel, z, time. The order in which these are added should be from 
    innermost iterated to outermost.

    Example: For a normal video acquisition, a video is taken with each 
    channel. Therefore, the innermost iterated is the time (frame number) and
    the outer is channel. Thus, t (number of frames) should be set first and 
    then the channel list.

    ## Methods:

    every method returns self (akin the builder design), except for build() 
    which returns an MM DefaultCoords object.

    #### channel_list(channels: list | tuple | str)
        adds channels as channel_names for summary metadata, sets intended 
        number of channels to len(channel_list), and adds "channel" to axis 
        order.

    #### z(z_num:int)
        adds "z" to axis order and sets intended number of z-slices to z_num

    #### t(t_num:int)
        adds "time" to axis order and sets intended number of time points to 
        t_num

    #### step(step_size:int)
        sets step_size (currently only used in z-stack acquisitions)
        
    #### interval_ms(interval_ms:int)
        sets the time interval between images (currently only should be used 
        in the standard video acquisition).

    #### build()
        returns MM DefaultSummaryMetadata object
    """
    def __init__(self):
        #unfortunately, can't just use a python list as axis_order() takes a 
        #java iterable object. Easiest one to grab and use is ArrayList.
        self._axis_order = JavaObject("java.util.ArrayList")
        #default 1 is set for each coord so that the axes appear in the 
        #metadata. If nothing or 0 are set for an axis and coords is built, 
        #it won't appear.
        self._intended_builder = ImageCoordsBuilder().c(1).z(1).t(1).p(1)
        self._summary_builder = studio.acquisitions().generate_summary_metadata().copy_builder()
    
    def channel_list(self, channels):
        self._axis_order.add(_C_AXIS)
        
        #unfortunately, can't just use a python list as channel_names() takes a 
        #java iterable object. Easiest one to grab and use is ArrayList.
        channel_array = JavaObject("java.util.ArrayList")
        if isinstance(channels, (list, tuple)):
            #Adds channel to intended builder for axis order
            self._intended_builder.c(len(channels))
            for channel in channels:
                channel_array.add(channel)
        elif isinstance(channels, str):
            #if channels is str, only one channel, so intended c is 1
            self._intended_builder.c(1)
            channel_array.add(channels)

        self._summary_builder.channel_names(channel_array)
        return self

    def z(self, num_z):
        self._axis_order.add(_Z_AXIS)
        self._intended_builder.z(num_z)
        return self

    def t(self, num_t):
        self._axis_order.add(_T_AXIS)
        self._intended_builder.t(num_t)
        return self

    def p(self, num_p):
        self._axis_order.add(_P_AXIS)
        self._intended_builder.p(num_p)
        return self
    
    def _start_date(self):
        self._summary_builder.start_date(str(datetime.now()))
        return self

    def step(self, step_size):
        """
        sets step size in summary metadata
        """
        self._summary_builder.z_step_um(step_size)
        return self
    
    def interval_ms(self, interval_ms):
        """
        sets interval_ms property in summary metadata
        """
        self._summary_builder.wait_interval(interval_ms)
        return self

    def _finalize_axis_order(self):
        #Default order is cztp, so added in this order if not already added
        for axis in (_C_AXIS, _Z_AXIS, _T_AXIS, _P_AXIS):
            if not self._axis_order.contains(axis):
                self._axis_order.add(axis)

    def build(self):
        self._finalize_axis_order()
        self._start_date()
        self._summary_builder.axis_order(self._axis_order)
        self._summary_builder.intended_dimensions(self._intended_builder.build())
        return self._summary_builder.build()


class ImageMetadataBuilder():
    """
    Python wrapper of the image metadata builder class in Micro-Manager 
    (see DefaultImageMetadataBuilder). Contains only the coords necessary to 
    have acceptable metadata (x_pos, y_pos, z_pos). Most of the metadata 
    (time image was received, camera used, pixel size, etc.) are set 
    automatically by Micro-Manager.

    see: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Metadata.Builder.html

    ## Methods:

    every method returns self (akin the builder design), except for build() 
    which returns an MM DefaultCoords object.

    #### x(x_pos:int)
        adds x_pos as x_position to image metadata

    #### y(y_pos:int)
        adds y_pos as y_position to image metadata

    #### z(z_pos:int)
        adds z_pos as z_position to image metadata

    #### build()
        returns MM DefaultImageMetadata object
    """

    def __init__(self, image=None):
        if image:
            self._meta_builder = studio.acquisitions().generate_metadata(image, True).copy_builder_preserving_uuid()
        else:
            self._meta_builder = studio.data().metadata_builder()

    def x(self, x_pos):
        """
        sets x_position_um in image metadata
        """
        self._meta_builder.x_position_um(x_pos)
        return self

    def y(self, y_pos):
        """
        sets y_position_um in image metadata
        """
        self._meta_builder.y_position_um(y_pos)
        return self

    def z(self, z_pos):
        """
        sets z_position_um in image metadata
        """
        self._meta_builder.z_position_um(z_pos)
        return self
    
    def build(self):
        return self._meta_builder.build()


class MultipageDatastore():
    """
    Python wrapper of MM multipage_tiff_datastore cass. Methods are the same 
    as MM counterparts except close() which supresses exceptions (only to 
    avoid the NullPointerException that's thrown when an empty datastore is 
    closed).

    See: https://micro-manager.org/apidoc/mmstudio/latest/org/micromanager/data/Datastore.html
    """
    def __init__(self, save_path):
        self._datastore = studio.data().create_multipage_tiff_datastore(save_path, True, False)
    
    def freeze(self):
        self._datastore.freeze()
    
    def put_image(self, image):
        self._datastore.put_image(image)
    
    def save(self):
        self.freeze()
        self._datastore.save()
    
    def set_summary_metadata(self, summary_metadata):
        self._datastore.set_summary_metadata(summary_metadata)
    
    def close(self):
        #If datastore has no images, throws a java NullPointerException. This supresses
        #that exception.
        with contextlib.suppress(Exception):
            self._datastore.close()


#misc functions
def set_channel(channel: str):
    core.set_config(CHANNEL, channel)


def snap_image():
    return studio.live().snap(False).get(0)


def get_channel_spec_list(channels: list):
    """
    gets channel_spec_list as pycromanager JavaObject of class
    java.util.ArrayList to be passed in to sequence settings.
    """
    channel_list = JavaObject("java.util.ArrayList")
    for channel in channels:
        spec_builder = studio.acquisitions().channel_spec_builder()
        spec_builder = spec_builder \
                           .channel_group(CHANNEL) \
                           .config(channel) \
                           .do_z_stack(True)
        channel_list.add(spec_builder.build())
    return channel_list


def set_position_list(xyz_positions: list[tuple[float, float, float]]):
    """
    sets the position list in Micro-Manager to positions in xyz_positions.
    """
    position_list = studio.positions().get_position_list()
    position_list.clear_all_positions()
    for pos in xyz_positions:
        multi_args = [core.get_xy_stage_device(), 
                      pos[0], 
                      pos[1], 
                      core.get_focus_device(), 
                      pos[2]]
        multi_position = pycromanager.JavaObject("org.micromanager.MultiStagePosition", args=multi_args)
        multi_position.set_label(str(pos))
        position_list.add_position(multi_position)
    studio.positions().set_position_list(position_list)
    
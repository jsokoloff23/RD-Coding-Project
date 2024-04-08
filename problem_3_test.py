"""
File used to test segmentation functionality for problem 3.
"""
import tifffile
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.color import label2rgb

#user parameters
filename = "Assoc_RDEng_test.tif"

image_stack = tifffile.TiffFile(filename)
image = image_stack.pages[0].asarray()


def test_segmentation():
    #apply threshold
    thresh = threshold_otsu(image)
    #label image regions
    label_image = label(image > thresh)
    #to make the background transparent, pass the value of `bg_label`,
    #and leave `bg_color` as `None` and `kind` as `overlay`
    image_label_overlay = label2rgb(label_image, image=image)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.imshow(image_label_overlay)

    for region in regionprops(label_image):
        #use regions in area range to remove objects that are too small to be
        #cells and too large to be single cells.
        if 100 <= region.area <= 2000:
                # draw rectangle around segmented coins
            minr, minc, maxr, maxc = region.bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                    fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(rect)
    plt.show()


def test_pixel_values():
    pixel_values = []
    for y in range(image.shape[1]):
        for x in range(image.shape[0]):
            pixel_value = image[x][y]
            if pixel_value > 0:
                pixel_values.append(pixel_value)

    plt.hist(pixel_values, bins=100)
    plt.show()
    
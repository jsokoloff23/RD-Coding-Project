"""
Problem 3 using skimage to segment and calculate eccentriity of cells.
"""
import tifffile
import matplotlib.pyplot as plt

from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops

#user parameters
filename = "Assoc_RDEng_test.tif"
hist_save_path = "problem 3 output/nucleus_eccentricity.png"

image_stack = tifffile.TiffFile(filename)
eccentricities = []
for page_num, page in enumerate(image_stack.pages):
    #labeling code adapted from this website:
    #https://scikit-image.org/docs/stable/auto_examples/segmentation/plot_label.html
    image = page.asarray()
    #Image set is clearly bimodal (see testing), so otsu's seems reasonable
    thresh = threshold_otsu(image)
    #label image with thresholded
    labeled = label(image > thresh)
    for region in regionprops(labeled):
        #use regions in area range to remove objects that are too small to be
        #cells and too large to be single cells.
        if 100 <= region.area <= 2000:
            eccentricities.append(region.eccentricity)

plt.hist(eccentricities, 40, color="orange")
plt.title("Cell Nucleus Eccentricities")
plt.xlabel("Ecentricity")
plt.ylabel("Nucleus Count")
plt.savefig(hist_save_path)

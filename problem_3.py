import tifffile
import matplotlib.pyplot as plt

from skimage.filters import threshold_otsu
from skimage.measure import label, regionprops
from skimage.morphology import closing, square
from skimage.color import label2rgb


filename = "Assoc_RDEng_test.tif"

image_stack = tifffile.TiffFile(filename)
eccentricities = []
for page_num, page in enumerate(image_stack.pages):
    image = page.asarray()
    #Image set is clearly bimodal (see testing), so otsu's seems reasonable
    thresh = threshold_otsu(image)
    #close to get rid of small speckles and non-cell objects
    thresholded = closing(image > thresh, square(3))
    #label image with thresholded
    labeled = label(thresholded)
    for region in regionprops(labeled):
        #use regions in area range to remove objects that are too small to be
        #cells and too large to be single cells.
        if 100 <= region.area <= 2000:
            eccentricities.append(region.eccentricity)

plt.hist(eccentricities, 30, color="orange")
plt.title("Cell Nucleus Eccentricities")
plt.xlabel("Eccentricities")
plt.ylabel("Nucleus Count")
plt.show()
# from matplotlib.backends.backend_agg import FigureCanvasAgg
# from matplotlib.figure import Figure
import numpy as np
import math
# from PIL import Image
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import json

with open('../SysMatConfig/Parameters.json') as json_file:
    parameters = json.load(json_file)

# Matrix dimension 90*90*32*6*8
NImgX_ = parameters["numImageX"]
NImgY_ = parameters["numImageY"]
NDetY_ = parameters["pixelSiPM"]
NModule_ = parameters["numPanel"]
NDetX_ = parameters["numDetectorLayer"]

addNoise = parameters["AddPoisson"]

radiusR = 20
bgRadius = radiusR*2
rDot = np.linspace(2, 4.5, 6)*radiusR/20

def addCircleArr(x, y, radius, imgInput, num):
    Npts = int(np.ceil(radius))
    print(num)
    totNpts = Npts*2-1
    patch = imgInput[int(x-Npts+1):int(x+Npts), int(y-Npts+1):int(y+Npts)]
    arrRadiiSqr = np.ones((totNpts, totNpts))*(radius**2)
    xy_prime = np.linspace(-Npts+1, Npts-1, totNpts)
    xv, yv = np.meshgrid(xy_prime, xy_prime)
    arrDistSqr = xv**2 + yv**2
    patch = np.where(np.sqrt(arrDistSqr) <= np.sqrt(arrRadiiSqr), num, patch)
    imgInput[int(x-Npts+1):int(x+Npts), int(y-Npts+1):int(y+Npts)] = patch


img = np.zeros((NImgX_, NImgY_))
phantom_activity = 1e9
outFname = ''
if addNoise:   
    contrasts = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0]
    voxel_bkg = phantom_activity/(3.14*((NImgX_*NImgY_) + (rDot[0]*rDot[0])*4 + (rDot[1]*rDot[1])*4 + (rDot[2]*rDot[2])*4 
                +(rDot[3]*rDot[3])*4 +(rDot[4]*rDot[4])*4 +(rDot[5]*rDot[5])*4 ))
    bg = voxel_bkg
    outFname = 'input/circle-phantom_noise.npz'
else:
    contrasts = range(1, 7)
    voxel_bkg = 1
    bg = 0.2
    outFname = 'input/circle-phantom.npz'

centerX = np.ceil(NImgX_/2)-1
centerY = np.ceil(NImgY_/2)-1
values = range(1, 7)
addCircleArr(centerX, centerY, bgRadius, img, bg)
disY = np.sin(np.arange(0, 6)*math.pi/3)*radiusR
disX = np.cos(np.arange(0, 6)*math.pi/3)*radiusR


for idx in range(0,6):
    addCircleArr(centerX+disX[idx], centerY+disY[idx], rDot[idx], img, contrasts[idx]*voxel_bkg)



# addCircleArr(centerX-displaceX,centerY,2,img,1)
# addCircleArr(centerX-displaceX,centerY,2,img,1)
# Plot the phantom

fig, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=320)

# pltTitle=ax.set_title('Phantom Image',fontsize=18)
pltTitle = ax.set_title('Contrast Phantom Image')
# xl=ax.set_xlabel("Image Voxel x", fontsize=12)
# yl=ax.set_ylabel("Image Voxel y" ,fontsize=12)
xl = ax.set_xlabel("Image Voxel x")
yl = ax.set_ylabel("Image Voxel y")
# plt.rcParams["font.family"] = "sans"
ax.grid(color='b', linestyle='-', linewidth=0.5, which='major')
ax.xaxis.set_major_locator(MultipleLocator(10))
ax.xaxis.set_minor_locator(MultipleLocator(1))
ax.yaxis.set_major_locator(MultipleLocator(10))
ax.yaxis.set_minor_locator(MultipleLocator(1))

xy = np.array([49, 49])
# imshow_obj=ax.imshow(img,extent=(0, NImgX_, 0, NImgX_),cmap=mpl.colormaps['copper'],interpolation='gaussian')
# imshow_obj = ax.imshow(img, extent=(0, NImgX_, 0, NImgX_),
#                        cmap=mpl.colormaps['copper'])
imshow_obj = ax.imshow(img.transpose(),
                       cmap=plt.get_cmap('nipy_spectral'),interpolation='None')
ax.set_xlim(-.5, NImgX_-.5)
ax.set_ylim(-.5, NImgY_-.5)
ax.set_aspect("equal")
cbar = fig.colorbar(imshow_obj)
# imshow_obj.set_clim(0, 1)
for idx in range(0, 6):
    ax.annotate(f'{values[idx]}', xy=(centerX+disX[idx],
                centerY+disY[idx]),  ha="left", va="bottom")
    x=np.linspace(0,NImgX_-1,NImgX_)
    ax.plot(x,(x-centerX)*np.tan(math.pi/3*range(0, 6)[idx])+centerY,color='r',linestyle='-.',linewidth=1)
plt.tight_layout()
plt.savefig('input/circle.png')
plt.cla()
# plt.show()
# Save the phantom as numpy npz file.

np.savez(outFname,img.astype(np.float32))
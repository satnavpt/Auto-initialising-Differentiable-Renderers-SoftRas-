import os
import re
from PIL import Image
import torch
import numpy as np
import soft_renderer as sr
import init_mesh as meshInit
import segment as seg
import build_mesh as meshBuild
import imageio
from pytorch3d.utils import ico_sphere

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(device)

segment = False
initMesh = True
cameraPred = False

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

# take a folder of images as input

input_folder = 'data/aloi/sil_grey_256/3'
images = []
for image in sorted_alphanumeric(os.listdir(input_folder)):
    im_file = os.path.join(input_folder, image)
    if segment: images.append(np.array(Image.open(im_file).resize((256,256)).convert('RGB')))
    else: images.append(np.array(Image.open(im_file).resize((256,256)).convert('RGBA')))
images = np.array(images)

# create a set of camera paremeters

cameras = []
for i in range(72):
    cameras.append([2.732, 0., i*5.])
cameras = np.array(cameras).astype('float32')

# estimate viewpoints

if cameraPred:
    pass

# segment images to produce silhouettes

if segment:
    s = seg.Segment(device)
    images = s.segmentMany(images).cpu()
images = np.transpose(images, (0,3,1,2))
# generate mesh prediction for silhouettes

# imageio.v2.imsave('test.png', np.transpose(images[0], (1,2,0)))

mesh_init = sr.Mesh.from_obj('data/obj/sphere/sphere_1922.obj')
if initMesh:
    mi = meshInit.Initialiser(images[0])
    mi.initialise(mesh_init)

# pass images, mesh init and viewpoints to softras to generate mesh

output_dir = 'data/results/buildMesh'
batch_size = 72
exp_name = '3-apricot-initmesh'
iters = 2000
m = meshBuild.Builder(exp_name, images, cameras, mesh_init, batch_size, output_dir, device, iters)
m.build_mesh()
#!/usr/bin/env python
 
'''
 Stitching sample
 ================
 
 Show how to use Stitcher API from python in a simple way to stitch panoramas
 or scans.
'''
 
from __future__ import print_function
import cv2 as cv  #opencv_contrib_python-4.0.0
import numpy as np
import argparse
import sys
import os
import time

start = time.time()
modes = (cv.Stitcher_PANORAMA, cv.Stitcher_SCANS)

parser = argparse.ArgumentParser(description='Stitching sample.')
parser.add_argument('--mode',
    type = int, choices = modes, default = cv.Stitcher_PANORAMA,
    help = 'Determines configuration of stitcher. The default is `PANORAMA` (%d), '
        'mode suitable for creating photo panoramas. Option `SCANS` (%d) is suitable '
        'for stitching materials under affine transformation, such as scans.' % modes)
parser.add_argument('--output', default = 'result.jpg',
    help = 'Resulting image. The default is `result.jpg`.')
parser.add_argument('-file', default = 'txtlists/files1.txt',
    help = 'Resulting image. The default is `txtlists/files1.txt`.')
#parser.add_argument('img', nargs='+', help = 'input images',default="/home/carvendy/dev/git/cv-test/images/")
args = parser.parse_args()

file = args.file
fp = open(file, 'r')
filenames = [each.rstrip('\r\n') for each in  fp.readlines()]
filenames = list(filter(lambda x: os.path.exists(x), filenames))
print(filenames)

# read input images
imgs = []
#imgs = [cv.resize(cv.imread(each),(480, 320)) for each in filenames]
for img_name in filenames:
    img = cv.imread(img_name)
    x,y = img.shape[0:2]
    img = cv.resize(img, (int(y / 4), int(x / 4)))
    if img is None:
        print("can't read image " + img_name)
        sys.exit(-1)
    imgs.append(img)

stitcher = cv.Stitcher.create(args.mode)
status, pano = stitcher.stitch(imgs)

if status != cv.Stitcher_OK:
    print("Can't stitch images, error code = %d" % status)
    sys.exit(-1)

cv.imwrite(args.output, pano);
print("stitching completed successfully. %s saved!" % args.output)
end = time.time()
print("cost time..."+str(end-start))
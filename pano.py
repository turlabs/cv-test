
import cv2
import sys
from matchers import matchers
import time
import os
import numpy as np
from skimage import filters
from imutils import paths
import argparse

class Stitch:
	def __init__(self, args):
		self.path = args
		fp = open(self.path, 'r')
		filenames = [each.rstrip('\r\n') for each in  fp.readlines()]
		# 过滤不存在图片
		filenames = list(filter(lambda x: os.path.exists(x), filenames))
		print(filenames)
		#filenames = self.filter_file(filenames)

		self.images = [cv2.resize(cv2.imread(each),(480, 320)) for each in filenames]
		self.count = len(self.images)
		self.left_list, self.right_list, self.center_im = [], [],None
		self.matcher_obj = matchers()
		self.prepare_lists()

	def prepare_lists(self):
		print ("Number of images : %d"%self.count)
		self.centerIdx = self.count/2 
		print ("Center index image : %d"%self.centerIdx)
		self.center_im = self.images[int(self.centerIdx)]
		for i in range(self.count):
			if(i<=self.centerIdx):
				self.left_list.append(self.images[i])
			else:
				self.right_list.append(self.images[i])
		print ("Image lists prepared")

	def variance_of_laplacian(self,image):
		# compute the Laplacian of the image and then return the focus
		# measure, which is simply the variance of the Laplacian
		return cv2.Laplacian(image, cv2.CV_64F).var()

	def filter_file(self,images) :
		print ('filer...blur')
		data = []
		ap = argparse.ArgumentParser()
		# ap.add_argument("-i", "--images", required=True,
		# help="path to input directory of images") 
		# ap.add_argument("-t", "--threshold", type=float, default=100.0,
		# help="focus measures that fall below this value will be considered 'blurry'")

		for imagePath in images:
			image = cv2.imread(imagePath)
			gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			fm = self.variance_of_laplacian(gray)
			text = "Not Blurry"
			if fm > 100:
				data.append(imagePath)
		
		return data
			

	def leftshift(self):
		# self.left_list = reversed(self.left_list)
		a = self.left_list[0]
		for b in self.left_list[1:]:
			H = self.matcher_obj.match(a, b, 'left')
			print ("Homography is : ", H)
			xh = np.linalg.inv(H)
			print ("Inverse Homography :", xh)
			ds = np.dot(xh, np.array([a.shape[1], a.shape[0], 1]));
			ds = ds/ds[-1]
			print ("final ds=>", ds)
			f1 = np.dot(xh, np.array([0,0,1]))
			f1 = f1/f1[-1]
			xh[0][-1] += abs(f1[0])
			xh[1][-1] += abs(f1[1])
			ds = np.dot(xh, np.array([a.shape[1], a.shape[0], 1]))
			offsety = abs(int(f1[1]))
			offsetx = abs(int(f1[0]))
			dsize = (int(ds[0])+offsetx, int(ds[1]) + offsety)
			print ("image dsize =>", dsize)
			
			tmp = cv2.warpPerspective(a, xh, dsize)
			tmp[offsety:b.shape[0]+offsety, offsetx:b.shape[1]+offsetx] = b
			
			# cv2.imshow("warped", tmp)
			# cv2.waitKey()
			#print(b.shape[0]+offsety)
			#print(b.shape[1]+offsetx)
			# try:
			# 	tmp = cv2.warpPerspective(a, xh, dsize)
			# 	tmp[offsety:b.shape[0]+offsety, offsetx:b.shape[1]+offsetx] = b
			# 	#tmp = self.mix_and_match(self.leftImage, tmp)
			# 	a = tmp
			# 	pass
			# except ValueError as identifier:
			# 	pass
			# finally:
			# 	pass
			

		self.leftImage = tmp

		
	def rightshift(self):
		for each in self.right_list:
			H = self.matcher_obj.match(self.leftImage, each, 'right')
			print ("Homography :", H)
			txyz = np.dot(H, np.array([each.shape[1], each.shape[0], 1]))
			txyz = txyz/txyz[-1]
			dsize = (int(txyz[0])+self.leftImage.shape[1], int(txyz[1])+self.leftImage.shape[0])
			tmp = cv2.warpPerspective(each, H, dsize)
			#cv2.imshow("tp", tmp)
			#cv2.waitKey()
			# tmp[:self.leftImage.shape[0], :self.leftImage.shape[1]]=self.leftImage
			tmp = self.mix_and_match(self.leftImage, tmp)
			print ("tmp shape",tmp.shape)
			print ("self.leftimage shape=", self.leftImage.shape)
			self.leftImage = tmp
		# self.showImage('left')



	def mix_and_match(self, leftImage, warpedImage):
		i1y, i1x = leftImage.shape[:2]
		i2y, i2x = warpedImage.shape[:2]
		print (leftImage[-1,-1])

		t = time.time()
		black_l = np.where(leftImage == np.array([0,0,0]))
		black_wi = np.where(warpedImage == np.array([0,0,0]))
		print (time.time() - t)
		print (black_l[-1])

		for i in range(0, i1x):
			for j in range(0, i1y):
				try:
					if(np.array_equal(leftImage[j,i],np.array([0,0,0])) and  np.array_equal(warpedImage[j,i],np.array([0,0,0]))):
						# print "BLACK"
						# instead of just putting it with black, 
						# take average of all nearby values and avg it.
						warpedImage[j,i] = [0, 0, 0]
					else:
						if(np.array_equal(warpedImage[j,i],[0,0,0])):
							# print "PIXEL"
							warpedImage[j,i] = leftImage[j,i]
						else:
							if not np.array_equal(leftImage[j,i], [0,0,0]):
								bw, gw, rw = warpedImage[j,i]
								bl,gl,rl = leftImage[j,i]
								# b = (bl+bw)/2
								# g = (gl+gw)/2
								# r = (rl+rw)/2
								warpedImage[j, i] = [bl,gl,rl]
				except:
					pass
		return warpedImage

	def trim_left(self):
		pass

	def showImage(self, string=None):
		if string == 'left':
			cv2.imshow("left image", self.leftImage)
			# cv2.imshow("left image", cv2.resize(self.leftImage, (400,400)))
		elif string == "right":
			cv2.imshow("right Image", self.rightImage)
		cv2.waitKey()

def mosaic(img, rect, size):
    (x1, y1, x2, y2) = rect
    w = x2 - x1
    h = y2 - y1
    i_rect = img[y1:y2, x1:x2]
    
    i_small = cv2.resize(i_rect, (size, size))
    i_mos = cv2.resize(i_small, (w, h), interpolation=cv2.INTER_AREA)
    
    img2 = img.copy()
    img2[y1:y2, x1:x2] = i_mos
    return img2


if __name__ == '__main__':
	try:
		args = sys.argv[1]
	except:
		args = "txtlists/files1.txt"
	finally:
		print ("Parameters : ", args)
	s = Stitch(args)
	s.leftshift()
	# s.showImage('left')
	s.rightshift()
	print ("done")
	cv2.imwrite("test12.jpg", s.leftImage)
	print ("image written")
	#cv2.destroyAllWindows()
	

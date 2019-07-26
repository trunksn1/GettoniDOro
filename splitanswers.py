# -- coding: utf-8 --
import cv2
import numpy as np

def splitanswers(img):

  positions = []
  threshold = 150
  flip      = 1
  
  #Average image along x to avoid false
  #flip due to letters
  averaged_im = np.mean(img,1)
  num_pixel   = len(averaged_im)
  
  for i in range(num_pixel):
    #Control is made bottom up to avoid question
    if averaged_im[-1-i] > threshold:
      while flip !=0 :
        positions.append(num_pixel-i)
        flip = 0
    else: 
      while flip !=1 :
        positions.append(num_pixel-i)
        flip = 1

  #First six positions correspond to y pixels
  #of beggining and end of answers box
  #orders is bottom up
  return positions[0:6]

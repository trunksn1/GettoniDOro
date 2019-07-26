# -- coding: utf-8 --
import cv2
import numpy as np

def splitanswers(img):
  flip = 1 
  positions = []
  for i in range(len(img[:,1135])):
    if img[-1-i,1335] > 220:
      while flip !=0 :
        positions.append(len(img[:,1135])-i)
        flip = 0
    else: 
      while flip !=1 :
        positions.append(len(img[:,1135])-i)
        flip = 1 
  return positions[0:6]
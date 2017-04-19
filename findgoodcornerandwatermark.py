from PIL import Image, ImageEnhance
from os import listdir, getcwd
from os.path import isfile, join
import numpy as np
import argparse
import cv2

imagepath = getcwd() + "\\Input\\"
watermarkpath = getcwd() + "\\Output\\"
logopath = "risshiki.png"

imagefiles = [f for f in listdir(imagepath) if isfile(join(imagepath, f))]

def reduce_opacity(im, opacity):
    
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def find_brightest_corner(im, mark, margin):

    #No sense going through the entire image. Find the corners and adjust them accordingly
    box1 = (margin, margin, mark.size[0]+margin , mark.size[1]+margin)
    corner1 = im.crop(box1)
    
    box2 = (im.size[0]-margin-mark.size[0],margin,im.size[0]-margin,mark.size[1]+margin)
    corner2 = im.crop(box2)

    box3 = (margin,im.size[1]-margin-mark.size[1],margin+mark.size[0],im.size[1]-margin)
    corner3 = im.crop(box3)

    box4 = (im.size[0]-margin-mark.size[0],im.size[1]-margin-mark.size[1],im.size[0]-margin,im.size[1]-margin)
    corner4 = im.crop(box4)
    
    
    cornerlayer = Image.new('RGBA', (mark.size[0]*2,mark.size[1]*2), (0,0,0,0))
    cornerlayer.paste(corner1,(0,0))
    cornerlayer.paste(corner2,(mark.size[0],0))
    cornerlayer.paste(corner3,(0,mark.size[1]))
    cornerlayer.paste(corner4,(mark.size[0],mark.size[1]))
    cornerlayer.save("temp.jpg")

    read_original = cv2.imread("temp.jpg")
    gray = cv2.cvtColor(read_original, cv2.COLOR_BGR2GRAY)

    if mark.size[0]<mark.size[1]:
        radius = mark.size[0]//2
    else:
        radius = mark.size[1]//2

    #Gaussian Radiuses can only be odd numbers
    if(radius%2==0):
        radius-=1

    gray = cv2.GaussianBlur(gray, (radius, radius), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(gray)

    #find out in which corner does max lie
    if maxLoc[0] <= mark.size[0] and maxLoc[1] <= mark.size[1]:
        return margin,margin
    elif maxLoc[0] >= mark.size[0] and maxLoc[1] <= mark.size[1]:
        return im.size[0]-margin-mark.size[0],margin
    elif maxLoc[0] <= mark.size[0] and maxLoc[1] >= mark.size[1]:
        return margin,im.size[1]-margin-mark.size[1]
    elif maxLoc[0] >= mark.size[0] and maxLoc[1] >= mark.size[1]:
        return im.size[0]-margin-mark.size[0],im.size[1]-margin-mark.size[1]

    
def watermark(im, mark, position, opacity=1):
    
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    # create a transparent layer the size of the image and draw the
    # watermark in that layer.
    layer = Image.new('RGBA', im.size, (0,0,0,0))
    layer.paste(mark, position)
    # composite the watermark with the layer
    return Image.composite(layer, im, layer)

def test(imagelocation, logolocation, savelocation, index,filename,margin):
    im = Image.open(imagelocation)
    mark = Image.open(logolocation)
    image_tuple = find_brightest_corner(im,mark,margin)
    result = watermark(im, mark, image_tuple, 0.5)
    result.save(watermarkpath + filename +".jpg")
    

    
if __name__ == '__main__':
    i = 1
    for imagek in imagefiles:
        test(imagepath+imagek,logopath,watermarkpath,i,imagek,20)
        i+=1




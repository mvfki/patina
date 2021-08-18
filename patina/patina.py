import cv2
import numpy as np
import base64

def _trim_uv(array):
    array[array>127] = 127
    array[array<-128] = -128
    return array

def _trim(array):
    array[array>255] = 255
    array[array<0] = 0
    return array

def patina(array):
    R = array[:,:,0].astype("float")
    G = array[:,:,1].astype("float")
    B = array[:,:,2].astype("float")
    y = _trim(np.floor((77*R + 150*G +  29*B)/256))
    u = _trim_uv(np.floor((-43*R -  85*G + 128*B) /256) - 1)
    v = _trim_uv(np.floor((128*R - 107*G -  21*B) /256) - 1)
    r1 = _trim(np.floor((65536*y           + 91881*v) / 65536))
    g1 = _trim(np.floor((65536*y - 22553*u - 46802*v) / 65536))
    b1 = _trim(np.floor((65536*y + 116130*u         ) / 65536))
    array[:,:,0] = r1
    array[:,:,1] = g1
    array[:,:,2] = b1
    array.astype(np.uint8)
    return array

def iter_patina(array, niter = 6):
    for i in range(niter):
        array = patina(array)

    return array

def jpg_comp(array, quality = 10):
    ecd, ecd2 = cv2.imencode(".jpg", array, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    array = cv2.imdecode(ecd2, cv2.IMREAD_UNCHANGED)
    return array

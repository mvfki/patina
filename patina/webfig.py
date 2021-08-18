import cv2
import numpy as np
import base64

def array_to_base64(img):
    retval, buf = cv2.imencode('.jpg', img)
    jpg_as_text = base64.b64encode(buf).decode('ascii')
    return "data:image/png;base64,"+jpg_as_text

def base64_to_array(img_base64):
    img_base64 = img_base64[22:]
    base64_decoded = base64.b64decode(img_base64)
    img = np.frombuffer(base64_decoded, np.uint8)
    array = cv2.imdecode(img, cv2.IMREAD_UNCHANGED)
    return array
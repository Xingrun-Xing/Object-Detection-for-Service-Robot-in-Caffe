import numpy as np  
import sys,os  
import cv2
caffe_root = '/home/xxr/caffe/'
sys.path.insert(0, caffe_root + 'python')  
import caffe  


net_file= '/home/xxr/caffe/examples/MobileNet-SSD-master/example/MobileNetSSD_deploy.prototxt'  
caffe_model='/home/xxr/caffe/examples/MobileNet-SSD-master/the_fifth_training.caffemodel'  

if not os.path.exists(caffe_model):
    print("MobileNetSSD_deploy.caffemodel does not exist,")
    print("use merge_bn.py to generate it.")
    exit()
net = caffe.Net(net_file,caffe_model,caffe.TEST)  

CLASSES = ('background',
           'kl', 'sp', 'dn', 'c',
           's', 'fbm', 'hly', 'myl','ala')


def preprocess(src):
    img = cv2.resize(src, (300,300))
    img = img - 127.5
    img = img * 0.007843
    return img

def postprocess(img, out):   
    h = img.shape[0]
    w = img.shape[1]
    box = out['detection_out'][0,0,:,3:7] * np.array([w, h, w, h])

    cls = out['detection_out'][0,0,:,1]
    conf = out['detection_out'][0,0,:,2]
    return (box.astype(np.int32), conf, cls)

def detect():
    cap=cv2.VideoCapture(0)
    ok,origimg=cap.read()
    img = preprocess(origimg)
    while cv2.waitKey(1)!=27 :
      ok,origimg=cap.read()
      img = preprocess(origimg)
    
      img = img.astype(np.float32)   
      img = img.transpose((2, 0, 1))

      net.blobs['data'].data[...] = img
      out = net.forward()       
      box, conf, cls = postprocess(origimg, out)

      for i in range(len(box)):
         if conf[i]>=0.7: 
           p1 = (box[i][0], box[i][1])
           p2 = (box[i][2], box[i][3])
           cv2.rectangle(origimg, p1, p2, (0,255,0))
           p3 = (max(p1[0], 15), max(p1[1], 15))
           title = "%s:%.2f" % (CLASSES[int(cls[i])], conf[i])
           cv2.putText(origimg, title, p3, cv2.FONT_ITALIC, 0.6, (0, 255, 0), 1)
      cv2.imshow("SSD", origimg)
    return True

detect()

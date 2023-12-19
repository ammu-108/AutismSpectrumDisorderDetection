# Import the libraries
import keras
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow.keras import utils
from PIL import *
from keras.preprocessing import image
from tensorflow import convert_to_tensor
from tensorflow.keras.metrics import top_k_categorical_accuracy
from tkinter import Label

classes=['Autism','Control']

def pre_process(img_path):
    img=utils.load_img(img_path,target_size=(224,224))
    img_tensor=utils.img_to_array(img)
    img_tensor=np.expand_dims(img_tensor,axis=0)
    img_tensor /=255
    return img_tensor
  

def detect(img_path,label):
    image=pre_process(img_path)

    model = keras.models.load_model("abide.h5",compile=False)

    predictions = model.predict(image)

    prediction=np.argmax(predictions,axis=1)

    result = classes[prediction[0]]

    label.config(text = 'Report: '+result)
    










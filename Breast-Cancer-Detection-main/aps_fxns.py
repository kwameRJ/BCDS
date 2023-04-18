from db import *
import tensorflow as tf
import numpy as np
import cv2
from PIL import Image
from model import download_model
from weights import download_weights

roles = ['administrator', 'staff']
medical_staff = ['radiologist', 'oncologist', 'surgeon', 'pathologist', 'nurse', 'physician assistant']
entity_dict = {
    "administrator": Administrator,
    "staff": Staff,
    "patient": Patient
    # Add more mappings as needed
}
id = AutoField(unique=True)
    
attributes_dict = {
    "user": ("id", "name","username", "password", "created_at"),
    "administrator": ("id", "name", "username", "password",  "created_at"),
    "staff": ("id", "name", "username", "password",  "created_at", "job_title"),
    "patient": ("id", "first_name", "last_name", "dob", "gender", "email", "phone", "address", "created_at"),
    "diagnostic_result": ("id", "patient","result_name", "result_value", "created_at"),
    }

df_dict = {
    "user": ("name","username", "password"),
    "administrator": ("name", "username", "password"),
    "staff": ("name", "username", "password", "job_title"),
    "patient": ("first_name", "last_name", "dob", "gender", "email", "phone", "address"),
    "diagnostic_result": ("patient","result_name", "result_value", "created_at"),
    }

  
def authenticate_user(username, password):
   try:
        user = read_user(username)
        if user and user.password == password: 
            return user
        else:
            return False
   except User.DoesNotExist:
        return False


def get_list(key, data):
    return [i.title() for i in data[key]]

def load_model():
        #download_model()
        model = tf.keras.models.load_model("model/model.h5")
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.00001, weight_decay=0.0001),
                      metrics=["accuracy"],
                      loss=tf.keras.losses.CategoricalCrossentropy(label_smoothing=0.1))
        #download_weights()
        model.load_weights("weights/modeldense1.h5")
        return model
    
    

def preprocess(image):
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    im = cv2.filter2D(image, -1, kernel)
    return im

model = load_model()
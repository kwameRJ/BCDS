import tensorflow as tf
import numpy as np
import cv2
import streamlit as st
from model import download_model
from weights import download_weights
from PIL import Image

def main(user = ""):
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
    
    
    column1, column2 = st.columns(2)
    # Upload image
    with column1:
        with st.spinner("Loading Models"):
            model = load_model()

        uploaded_file = st.file_uploader("Upload mammology image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            st.image(uploaded_file)
    
        # Display results
        class_name = ['Benign with Density=1', 'Malignant with Density=1', 'Benign with Density=2',
                      'Malignant with Density=2', 'Benign with Density=3', 'Malignant with Density=3',
                      'Benign with Density=4', 'Malignant with Density=4']
        
        
    
        
        
        if st.button("Predict"):
            with column2:
                # Load and preprocess image
                with st.spinner("Processing Image..."):
                    image = Image.open(uploaded_file)
                    image = np.array(image)
                    image = preprocess(image)
                    image = image / 255.0
                    im = image.reshape(-1, 224, 224, 3)

                # Make prediction
                with st.spinner("Generating Prediction"):
                    pred = model.predict(im)[0]
                st.snow()
                results = list(zip(class_name, pred))
                results.sort(key=lambda x:x[1], reverse=True)
                st.subheader("Results")
                st.divider()
                level = f"Prediction: {round(float(results[0][1])*100,2)}%"
                cancer = f"Cancer Type: {results[0][0]}"
                
                st.info(cancer)
                st.warning(level)
                with st.expander("See Detailed Results"):
                    for i in results:
                        percent = float(i[1])
                        text = f"{i[0]} {round(percent*100,2)}%"
                        st.progress(percent, text = text)
            if user:
                if st.button("Save Results"):
                    pass
                
        
    
if __name__ == '__main__':
    main()

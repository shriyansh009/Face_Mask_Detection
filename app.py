import os
from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image
import numpy as np
import cv2
from tensorflow.keras.models import load_model
import base64

app = Flask(__name__)
app.secret_key = 'any_secret_key'
UPLOAD_FOLDER = 'static/uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


model = load_model("Model/mask_detector.keras")  

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if 'image' in request.files and request.files['image'].filename != '':
            image_file = request.files['image']
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(filepath)

        elif 'camera_image' in request.form:
            camera_data = request.form['camera_image']
            if "," in camera_data:
                _, encoded = camera_data.split(",", 1)
            else:
                encoded = camera_data
            img_bytes = base64.b64decode(encoded)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'captured.jpg')
            with open(filepath, "wb") as f:
                f.write(img_bytes)
        else:
            return redirect(url_for('index'))

    
        img = cv2.imread(filepath)
        if img is None:
            return f"Error: Could not load image from {filepath}"
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, (128, 128)) # model  is train on 128x128 
        img_array = img_resized.astype("float32") / 255.0
        img_array = np.expand_dims(img_array, axis=0)

       
        output = model.predict(img_array)[0]
        if len(output) > 1: 
            pred_class = np.argmax(output)
            confidence = float(np.max(output))
            label = "Mask" if pred_class == 0 else "No Mask"
        else: 
            confidence = float(output[0])
            label = "Mask" if confidence > 0.5 else "No Mask"
            confidence = confidence if label == "Mask" else 1 - confidence

        result = {"prediction": label, "confidence": confidence}
        session['result'] = result
        session['image_url'] = filepath
        return redirect(url_for('result'))

    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/result')
def result():
    return render_template('result.html',
                           result=session.get('result'),
                           image_url=session.get('image_url'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

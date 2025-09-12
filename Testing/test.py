import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input


model = load_model("Model/mask_detector.keras")


# img_path = "Testing/images/test1.jpg"
img_path = "Testing/images/test2.jpeg"
image = cv2.imread(img_path)
image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image_resized = cv2.resize(image, (128,128))


inp = image_resized.astype("float32") / 255.0
inp = np.expand_dims(inp, axis=0)


prob = model.predict(inp)[0][0]
label = "Mask" if prob > 0.5 else "No Mask"
print(f"Prediction: {label} (prob={prob:.4f})")

import os
from flask import Flask, render_template, request, session, redirect, url_for
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import json
import io
import re
import base64


# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

app = Flask(__name__)
app.secret_key = 'any_secret_key'
UPLOAD_FOLDER = 'static/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Gemini model
model = genai.GenerativeModel('models/gemini-1.5-flash')

PROMPT = """
You are a medical assistant. Analyze the image of a visible human health condition
and reply strictly in this JSON format only:
{
  "diagnosis": "string",
  "description": "string",
  "symptoms":"string",
  "home_remedies": ["string1", "string2"],
  "medicines": ["string1", "string2"]
}
Do NOT include markdown, explanations, or text outside the JSON object.
"""

def extract_json(text):
    try:
        json_str = re.search(r'\{.*\}', text, re.DOTALL).group()
        return json.loads(json_str)
    except Exception:
        raise ValueError("Invalid JSON in Gemini response.")

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
            header, encoded = camera_data.split(",", 1)
            img_bytes = base64.b64decode(encoded)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'captured.jpg')
            with open(filepath, "wb") as f:
                f.write(img_bytes)
        else:
            return redirect(url_for('index'))

        image = Image.open(filepath).convert("RGB")
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        img_bytes = img_byte_arr.getvalue()

        response = model.generate_content([
            PROMPT,
            {
                "mime_type": "image/jpeg",
                "data": img_bytes
            }
        ])
        result = extract_json(response.text)

        session['result'] = result
        session['image_url'] = filepath
        return redirect(url_for('result'))

    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/result')
def result():
    return render_template('result.html', result=session.get('result'), image_url=session.get('image_url'))

if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0") 

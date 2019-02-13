import os
from flask import send_file, request, jsonify
from flask import Flask
from flask_cors import CORS
import visualize_prediction as V
import pandas as pd
import warnings
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt
import base64
import json
from io import BytesIO
from PIL import Image


app = Flask(__name__)
CORS(app)
ENCODING = 'utf-8'
# create the folders when setting up your app
os.makedirs(os.path.join(app.instance_path), exist_ok=True)

@app.route('/predict', methods=['POST'])
def predict():
    print(request)
    print("the request files are")
    print(request.files)
    file = request.files['file']
    file.filename="our.jpg"
    print(file.filename)
    file.save(file.filename)
    testimage = scipy.misc.imresize(scipy.misc.imread(file),(150,150))
    print(testimage.shape)
    testimage = testimage.reshape((1,) + testimage.shape)
    prediction = loaded_model.predict(testimage).astype(float)
    print(prediction)
    return jsonify({ 'classification': { 'cat': prediction[0][0], 'dog' : 1-prediction[0][0]} })

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      #f = request.files['file']
      print("the request is")
      #print(request)
      content = request.json
      #print(content)

      file = content['base64img']
      diagnosis = content['diagnosis']

      starter = file.find(',')
      image_data = file[starter+1:]
      image_data = bytes(image_data, encoding="ascii")
      f = Image.open(BytesIO(base64.b64decode(image_data)))

      # when saving the file
      # This is hardcoded to work with Pneumonia need to fix for all diseases.
      f.save(os.path.join(app.instance_path, secure_filename('00000165_001.png')))
      # prediction
      STARTER_IMAGES=False
      PATH_TO_IMAGES = 'instance'
      PATH_TO_MODEL = "pretrained/checkpoint"
      LABEL="Pneumonia"
      ## Need to figure out how to change the hardcoded values in order to change the diagnosis type
      #LABEL=request.form['diagnosis']
      POSITIVE_FINDINGS_ONLY=True
      dataloader,model= V.load_data(PATH_TO_IMAGES,LABEL,PATH_TO_MODEL,POSITIVE_FINDINGS_ONLY,STARTER_IMAGES)
      print("Cases for review:")
      print(len(dataloader))
      preds, imglocation=V.show_next(dataloader,model, LABEL)
      print(preds)
      print(imglocation)
      encodedimage = ""

      with open(imglocation, "rb") as image_file:
         encodedimage = base64.b64encode(image_file.read())
      #preds

      print(encodedimage)
      base64_string = encodedimage.decode(ENCODING)

      # plt.savefig(preds, format='png')
      # preds.seek(0)
      # response=make_response(preds.getvalue())
      # response.headers['Content-Type'] = 'image/png'
      # preds.close()
      #return send_file(preds, mimetype='image/png')
      #return response
      jsonfiles = json.loads(preds.to_json())
      return jsonify({ 'prediction': jsonfiles, 'encodedimage': base64_string  })
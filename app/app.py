# -*- coding: utf-8 -*-

import base64, os, uuid
import services
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify
import tefla.predict as predict_mnist
from config import Config

app = Flask(__name__)
conf = Config()

@app.route("/")
def mainpage():
    if request.method == "POST":
        print(request.form)
    if request.method == "GET":
        return render_template("index.html")

@app.route("/hindi")
def hindipage():
    if request.method == "POST":
        print(request.form)
    if request.method == "GET":
        return render_template("index.html")


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    if request.method == "POST":
        image_data64 = request.json['image']
        #print(request.json['model'])
        if request.json['model'] == 'hindi':
            weights = conf.devnagri_char_weights
            model_file = services.mnist_model_char_hindi
            devnag_char_dict = {"0": "क", "1": "ख", "2": "ग", "3": "घ", "4": "ङ", \
								"5": "च", "6": "छ", "7":"ज", "8":"झ", "9":"ञ", \
								"10":"ट","11":"ठ","12":"ड","13":"ढ","14":"ण", \
								"15":"त", "16":"थ", "17":"द", "18":"ध","19":"न", \
								"20":"प","21":"फ","22":"ब","23":"भ", "24":"म", \
								"25":"य", "26":"र","27":"ल","28":"व", \
								"29":"श","30":"ष","31":"स", "32":"ह", \
								"33":"क्ष", "34":"त्र","35":"ज्ञ"}						
        else:
            weights = conf.all_num_weights
            model_file = services.mnist_model_num_all
        image_data64 = image_data64.split(",")[1]
        image_filename = str(uuid.uuid4()) + ".tiff"

        image = open(image_filename, "wb")
        image.write(base64.b64decode(image_data64))
        image.close()

        with Image.open(image_filename).convert('L') as image:
            image = image.resize([28, 28])
            img = Image.fromarray(np.uint8(image))
            img.save(image_filename)

        image_path_array = np.array([image_filename])
        predictions = predict_mnist.predict(model=model_file.model,
                                            model_def=model_file,
                                            output_layer="predictions",
                                            cnf=services.mnist_cnf.cnf,
                                            weights_from=weights,
                                            images=image_path_array,
                                            sync=True,
                                            convert=False,
                                            image_size=28,
                                            predict_type="1_crop")
        prediction = np.argmax(predictions)
        if request.json['model'] == 'hindi':
            main_result = [devnag_char_dict[str(prediction)], "Hindi"]
        else:
            if prediction > 9:
                prediction = prediction -10
                main_result = [prediction,"Hindi"]
            else:
                main_result = [prediction,"English"]
        print("%s in %s" % (main_result[0], main_result[1]))

        #Cleaning Images
        os.remove(image_filename)

    return jsonify(main_result)

if __name__ == "__main__":
    app.run(debug=True)

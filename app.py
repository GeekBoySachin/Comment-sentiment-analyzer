# doing necessary imports
from flask import Flask, render_template, request, url_for, redirect
from flask_cors import CORS, cross_origin
from scrapper import Scrapper
from sentiment.pipeline.prediction_pipeline import Predict
from transformers import logging

logging.set_verbosity_error()


app = Flask(__name__)

@cross_origin()
@app.route('/home', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        youtube_video_link = request.form['content'].replace(" ", "")
        if "?v=" not in youtube_video_link:
            return render_template('home.html', status="No")
        scrapper_object = Scrapper(youtube_video_link)
        result = scrapper_object.process_request()
        comment_data = result[-1]
        pred_obj = Predict(comment_data)
        names,comments,labels,scores = pred_obj.predict_sentiment()
        output = {"yoututber":result[1],"title":result[2],"names":names,"labels":labels,"scores":scores,"comments":comments,"rows":len(comments)}
        del scrapper_object
        del pred_obj
        return render_template('results.html',output=output)
    else:
        return render_template('home.html')


if __name__ == "__main__":
    app.run(host="127.0.0.1",port=5000)

# from transformers import pipeline
# sentiment_pipeline = pipeline("sentiment-analysis")
# data = ["I love you", "I hate you"]
# print(sentiment_pipeline(data))

from flask import Flask, render_template, request, url_for, redirect
from flask_cors import CORS, cross_origin
from scrapper import Scrapper
from sentiment.pipeline.prediction_pipeline import Predict
from logger import logging
from exception import ScrapperException
import sys

scrapper_object = Scrapper("https://www.youtube.com/watch?v=TO-_3tck2tg")
result = scrapper_object.process_request()
comment_data = result[-1]
pred_obj = Predict(comment_data)
names,comments,labels,scores = pred_obj.predict_sentiment()
print(names,comments,labels,scores)
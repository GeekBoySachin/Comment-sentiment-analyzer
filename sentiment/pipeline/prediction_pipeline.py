from transformers import pipeline
from sentiment.component.data_transform import DataTransform
import pandas as pd

class Predict:
    def __init__(self,data:list)-> tuple:
        self.data = data

    def predict_sentiment(self):
        obj = DataTransform(self.data)
        names,comments = obj.convert_input_data_into_lists()
        sentiment_pipeline = pipeline("sentiment-analysis")
        df = pd.DataFrame(sentiment_pipeline(comments))
        return names,comments,list(df['label']),list(df['score'])


if __name__=="__main__":
    obj = Predict(["i hate game"])
    obj.predict_sentiment()
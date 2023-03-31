import pandas as pd

class DataTransform:
    def __init__(self,input_data:list):
        self.input_data = input_data

    def convert_input_data_into_lists(self):
        comments = []
        names = []
        # print(self.input_data)
        for i in self.input_data:
            # print(i)
            for k,v in i.items():
                names.append(k)
                comments.append(v)
        return names,comments
    
    
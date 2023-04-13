import re
import pandas as pd
import string
import pathlib as Path
import mysql.connector
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from nltk.stem.porter import PorterStemmer
import streamlit as st
import time as tt

class whatsapp_cleaner():
    def __init__(self):
        pass

    def dict_to_df(self, df):
        df = pd.DataFrame.from_dict(df)
        return df
    
    def preprocessor(self, review):
        review = review.lower()
        review = re.sub(r'\d+', '', review)
        review = re.sub('[^a-zA-Z]', ' ', review)
        pattern = re.compile(r'\s+')
        review = re.sub(pattern, ' ', review)
        return review
    
    def stemming(self, review):
        ps = PorterStemmer()
        review = review.split(' ')
        review = [ps.stem(word) for word in review if word not in stopwords.words('english')]
        return ' '.join(review)
    
    def remove_spaces(self, review):
        pattern = re.compile(r'\s+')
        review = re.sub(pattern, ' ', review)
        return review

    def get_cleaned_whatsapp_data(self, data):
        whatsapp_clean_data = {
        'Date':[],
        'Time': [],
        'Username': [],
        'Message': []
        }    
        chat_data_ordered = [] 
        for line in data:
            line = line.replace('\u202a','')
            line = line.replace('\xa0','')
            line = line.replace('\u202c','')
            line = line.replace('\n','')
            line = line.replace('\u200e','')
            for char in line:
                if char=='[':
                    chat_data_ordered.append(line)
                    break
                else:
                    chat_data_ordered[-1] = chat_data_ordered[-1]+line
                    break    
        for string in chat_data_ordered:
            try:
                date_time_pattern = re.compile(r'\[(.+?)\]')
                date_time = re.search(date_time_pattern, string).group(1)
                date, time_am_am = date_time.split(", ")

                time = time_am_am.split(" ")[0]

                username_pattern = re.compile(r'\] (.+?):')
                username = re.search(username_pattern, string).group(1)

                message = string.split(": ", 1)[1]

                whatsapp_clean_data['Date'].append(date)
                whatsapp_clean_data['Time'].append(time)
                whatsapp_clean_data['Username'].append(username)
                whatsapp_clean_data['Message'].append(message)
            except:
                pass
        df = self.dict_to_df(whatsapp_clean_data)
        df['Date'] = pd.to_datetime(df['Date'])
        df['Message'] = df['Message'].apply(lambda x: self.preprocessor(x))
        df['stemmed_reviews'] = df['Message'].apply(lambda x: self.stemming(x))
        df.drop(['Time'], axis=1, inplace=True)
        df = df.rename(columns={'Message':'reviews'})
        df.drop(df[df['stemmed_reviews']==' '].index, inplace=True)
        df.reset_index(inplace=True, drop=True)
        df.dropna(inplace=True)
        return df
    

        

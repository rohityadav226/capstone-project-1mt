import pandas as pd
import numpy as np
from typing import Optional
import tensorflow as tf
from tensorflow import keras
from whatsapp_db import whatsappdb
import streamlit as st


class predictor():
    def __init__(self):
        self.model = keras.models.load_model("binary_unigram_model.keras", compile=False) 
        self.model.compile(optimizer="rmsprop", loss="categorical_crossentropy", metrics=["accuracy"])

    def preprocess(self, df):
        text_vectorization_unigram_binary = keras.layers.TextVectorization(max_tokens=15000, output_mode='binary')
        text_vectorization_unigram_binary.adapt(df['stemmed_reviews'].to_numpy())
        tokenized = text_vectorization_unigram_binary(df['stemmed_reviews'])
        if tokenized.shape[1] != 15000:
            padded_data = np.zeros((tokenized.shape[0], 15000))
            for i, row in enumerate(np.array(tokenized)):
                padded_data[i, :row.shape[0]] = row
            return padded_data
        else:
            return tokenized
        
    def make_prediction(self, data):
        predictions = self.model.predict(data)
        labels = tf.argmax(predictions, axis=1)
        return list(labels.numpy())

    def predict(self, whatsapp: Optional[pd.DataFrame] = None, facebook: Optional[pd.DataFrame] = None):

        #if facebook is None and whatsapp is not None:
        #    df = whatsapp.copy()
        #    df = whatsapp[['reviews', 'stemmed_reviews']]
       # else:
        date = pd.to_datetime(whatsappdb().get_timestamp())
        date = pd.to_datetime(date)
        whatsapp['Date'] = pd.to_datetime(whatsapp['Date'])
        whatsapp2 = whatsapp[whatsapp['Date']>date]
        whatsapp2 = whatsapp2[['reviews', 'stemmed_reviews']]
        facebook = facebook[['reviews', 'stemmed_reviews']]
        df = pd.concat([whatsapp2, facebook])
        if df.shape[0]>0:
            df.dropna(inplace=True)   
            df = df.sample(frac=1)
            pred_data = self.preprocess(df)
            pred = self.make_prediction(pred_data)
            df['rating'] = pred
            return df
        else:
            st.write('Data is insufficient for analysis')






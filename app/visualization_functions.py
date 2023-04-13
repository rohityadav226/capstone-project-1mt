import pandas as pd
import pycountry
import re
import stanza
import nltk
from wordcloud import WordCloud
from nltk.stem import PorterStemmer
import matplotlib.pyplot as plt
from english_words import get_english_words_set
nltk.download('words')
from nltk.corpus import words
import streamlit as st
import warnings
warnings.filterwarnings('ignore')
stanza.download('en')
st.set_option('deprecation.showPyplotGlobalUse', False)

class visual_preprocessor():
    def __init__(self):
        self.ps = PorterStemmer()
        self.countries = []
        for country in pycountry.countries:
            self.countries.append(country.name)
        self.nlp = stanza.Pipeline(lang='en', processors='tokenize,ner')
        self.english_words = set(words.words())
        self.web2lowerset = get_english_words_set(['web2'], lower=True)
        self.english_words_combined = list(set(list(self.english_words) + list(self.web2lowerset)))
        self.partial_words = [word[0:5] for word in self.english_words_combined]
        
    
    def unique_word_count(self, df, column_name):
        all_words = (' '.join(list(df[column_name]))).split(' ')
        unique_words = list(set(all_words))
        unique_word_count = {'word':[], 'count':[]}
        for word in unique_words:
            unique_word_count['word'].append(word)
            unique_word_count['count'].append(all_words.count(word))
        unique_word_count_df = pd.DataFrame.from_dict(unique_word_count)
        return unique_word_count_df

    def remove_country_and_names(self, text):
        pattern = '|'.join(self.countries)
        text_1 = re.sub(pattern,'', text, flags= re.IGNORECASE)
        doc = self.nlp(text_1)
        for ent in doc.entities:
            if ent.type == "PERSON":
                text = text.replace(" " + ent.text + " ", " ")
                text = text.replace(ent.text + " ", "")
                text = text.replace(" " + ent.text, "")
        return text
    
    def check_word(self, message):
        message = message.split(' ')
        temp = []
        for word in message:
            if len(word) > 2 and ((word in self.english_words_combined) or (word[0:5] in self.partial_words)):
                temp.append(word)
            else:
                pass
        if temp:
            return ' '.join(temp)
        else:
            return 'NaN'
    
    def stemming(self, review):
        review = review.split(' ')
        review = [self.ps.stem(word) for word in review]
        return ' '.join(review)
    
    def remove_spaces(self, review):
        pattern = re.compile(r'\s+')
        review = re.sub(pattern, ' ', review)
        return review
    
    def word_cloud(self, destem_dict, df):
        text = ' '.join([destem_dict[word] for sen in df['stemmed_reviews'] for word in sen.split(' ')])   
        word_cloud = WordCloud(collocations=False, background_color = 'white').generate(text)
        plt.figure(figsize=(10,6))
        plt.imshow(word_cloud, interpolation='bilinear')
        plt.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot()

    def remove_common(self, words_to_remove, review):
        return ' '.join([word for word in review.split(' ') if word not in words_to_remove])
    
    def preprocess_data(self, data):
        data['reviews_new'] = data['reviews'].apply(lambda x: self.remove_country_and_names(x))
        data = data[['reviews_new', 'rating']]
        data.dropna(inplace=True)
        data['reviews_new'] = data['reviews_new'].apply(lambda x: self.remove_spaces(x))
        data['reviews_new'] = data['reviews_new'].apply(lambda x: self.check_word(x))
        data = data.drop(data[data['reviews_new']=='NaN'].index)
        data['stemmed_reviews'] = data['reviews_new'].apply(lambda x: self.stemming(x))
        word_df = self.unique_word_count(data, 'reviews_new')
        destem_dict = {}
        for word in list(word_df['word']):
            destem_dict[self.ps.stem(word)] = word
        rat_1 = data.loc[data['rating']==0]
        rat_2 = data.loc[data['rating']==1]
        rat_3 = data.loc[data['rating']==2]
        df_1_count = self.unique_word_count(rat_1, 'stemmed_reviews')
        df_2_count = self.unique_word_count(rat_2, 'stemmed_reviews')
        df_3_count = self.unique_word_count(rat_3, 'stemmed_reviews')
        merged_df = pd.merge(df_1_count, df_2_count, on='word', how='inner')
        merged_df = pd.merge(merged_df, df_3_count, on='word', how='inner')
        merged_df.sort_values(by='count', ascending=False)
        words_to_remove = list(merged_df['word'])
        words_to_remove = ['thank', 'appreciate', 'appreciates', 'welcom', 'thanks', 'great', 'good', 'glad', 'happy', 'happi','bless', 'thrill', 'partak', 'bunch', 'goodwil', 'relationship', 'congratul', 'pleas']
        rat_2['stemmed_reviews'] = rat_2['stemmed_reviews'].apply(lambda x: self.remove_common(words_to_remove, x))
        rat_2 = rat_2.drop(rat_2[rat_2['stemmed_reviews']==''].index)
        rat_3['stemmed_reviews'] = rat_3['stemmed_reviews'].apply(lambda x: self.remove_common(words_to_remove, x))
        rat_3 = rat_3.drop(rat_3[rat_3['stemmed_reviews']==''].index)
        return destem_dict, rat_1, rat_2, rat_3

import pandas as pd
import numpy as np
import seaborn as sns
import nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import words
nltk.download('words')
nltk.download('stopwords')
from nltk.corpus import stopwords
import tensorflow as tf
from tensorflow.keras.layers import TextVectorization
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from english_words import get_english_words_set
from sklearn.metrics.pairwise import cosine_similarity
from scipy.cluster import hierarchy
from scipy.cluster.hierarchy import fcluster


class datapreprocessor():
    def __init__(self):
        self.stopwords_updated = stopwords.words('english')
        self.stopwords_updated.append('nbsp')
        self.english_words = set(words.words())
        self.web2lowerset = get_english_words_set(['web2'], lower=True)
        self.english_words_combined = list(set(list(self.english_words) + list(self.web2lowerset)))
        self.partial_words = [word[0:5] for word in self.english_words_combined]
        self.ps = PorterStemmer()

    def remove_stopword(self, review):
        review = review.split(' ')
        review = [word for word in review if word not in self.stopwords_updated]
        return ' '.join(review)

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
    
    def unique_word_count(self, df):
        all_words = (' '.join(list(df['stemmed_reviews']))).split(' ')
        unique_words = list(set(all_words))
        unique_word_count = {'word':[], 'count':[]}
        for word in unique_words:
            unique_word_count['word'].append(word)
            unique_word_count['count'].append(all_words.count(word))
        unique_word_count_df = pd.DataFrame.from_dict(unique_word_count)
        return unique_word_count_df
    
    def get_destem_dict(self, unique_words):
        destem_dict = {}
        for word in unique_words['word']:
            destem_dict[self.ps.stem(word)] = word
        return destem_dict

    
    def get_tfidfmatrix(self, df, column_name):
        text_vectorization_unigram_tfidf = TextVectorization(output_mode = 'tf-idf')
        with tf.device('/cpu:0'):
            text_vectorization_unigram_tfidf.adapt(df[column_name].to_numpy())
        df['vectors'] = df[column_name].apply(lambda x: text_vectorization_unigram_tfidf(x))
        return df
    
    def get_cosine_similarity_matrix(self, df, column_name):
        embeddings = np.vstack(df[column_name].values)
        similarity_matrix = cosine_similarity(embeddings)
        return similarity_matrix
    
    def perform_hierarchal_clustring(self, similarity_matrix):
        distance_matrix = 1 - similarity_matrix
        linkage_matrix = hierarchy.linkage(distance_matrix, method='complete')
        return linkage_matrix

    def create_clusters(self, df, linkage_matrix):
        for i in range(1,1000):
            try:
                threshold = i
                cluster_labels = fcluster(linkage_matrix, threshold, criterion='distance')
                cluster_names = {1: 'Cluster 1', 2: 'Cluster 2', 3: 'Cluster 3'}
                cluster_labels_named = [cluster_names[label] for label in cluster_labels]
                break
            except:
                pass
        df['labels'] = cluster_labels_named
        return df
    
    def seperate_clusters(self, df):
        df1 = df.loc[df['labels'] == 'Cluster 1']
        df2 = df.loc[df['labels'] == 'Cluster 2']
        df3 = df.loc[df['labels'] == 'Cluster 3']
        return df1, df2, df3
    
    def get_common_words(self, df1, df2, df3):
        df1_count = self.unique_word_count(df1)
        df2_count = self.unique_word_count(df2)
        df3_count = self.unique_word_count(df3)
        merged_df = pd.merge(df1_count, df2_count, on='word', how='inner')
        merged_df = pd.merge(merged_df, df3_count, on='word', how='inner')
        words_to_remove = list(merged_df['word'])
        return words_to_remove

    def remove_common_words(self, df, words_to_remove):
        def remove_common(review):
            return ' '.join([word for word in review.split(' ') if word not in words_to_remove])
        df['stemmed_reviews'] = df['stemmed_reviews'].apply(lambda x: remove_common(x))
        df = df.drop(df[df['stemmed_reviews']==''].index)
        return df

    def preprocess_data(self, whatsapp_df, facebook_df):
        whatsapp_df['valid_words'] = whatsapp_df['Message'].apply(lambda x: self.check_word(x))
        whatsapp_df['valid_words'] = whatsapp_df['valid_words'].apply(lambda x: self.remove_stopword(x))
        facebook_df['valid_words'] = facebook_df['fb_comments'].apply(lambda x: self.check_word(x))
        facebook_df['valid_words'] = facebook_df['valid_words'].apply(lambda x: self.remove_stopword(x))
        facebook_df = facebook_df.drop(facebook_df[facebook_df['valid_words']=='NaN'].index)
        whatsapp_df = whatsapp_df.drop(whatsapp_df[whatsapp_df['valid_words']=='NaN'].index)
        final_df = pd.DataFrame(pd.concat([whatsapp_df['valid_words'], facebook_df['valid_words']], axis=0, ignore_index=True,))
        final_df = final_df.rename(columns={'valid_words': 'reviews'})
        final_df = final_df[['reviews']]
        final_df['stemmed_reviews'] = final_df['reviews'].apply(lambda x: self.stemming(x))

        final_df = self.get_tfidfmatrix(final_df, 'stemmed_reviews')
        similarity_matix = self.get_cosine_similarity_matrix(final_df, 'vectors')
        linkage_matrix = self.perform_hierarchal_clustring(similarity_matix)
        final_df = self.create_clusters(final_df, linkage_matrix)
        df1, df2, df3 = self.seperate_clusters(final_df)
        # words_to_remove = self.get_common_words(df1, df2, df3)
        unique_words_df1 = self.unique_word_count(df1)
        unique_words_df2 = self.unique_word_count(df2)
        unique_words_df3 = self.unique_word_count(df3)
        length_dict = {'df1': len(unique_words_df1['word']), 'df2': len(unique_words_df2['word']), 'df3': len(unique_words_df3['word'])}
        largest = sorted(length_dict.items(), key=lambda x: x[1], reverse=True)[:2]
        if largest[0][0] == 'df1' or largest[1][1] == 'df1':
            df1 = self.remove_common_words(self, df1, words_to_remove)
        if largest[0][0] == 'df2' or largest[1][1] == 'df2':
            df2 = self.remove_common_words(self, df2, words_to_remove)
        if largest[0][0] == 'df3' or largest[1][1] == 'df3':
            df3 = self.remove_common_words(self, df3, words_to_remove) 
        return final_df, df1, df2, df3, unique_words_df1, unique_words_df2, unique_words_df3


import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from wordcloud import WordCloud
from html_css import design
from whatsapp_chat_transformer import whatsapp_cleaner
from facebook_scrapper import FacebookScrapper
import base64
import mysql.connector
from visualization_functions import visual_preprocessor
from nltk.stem import PorterStemmer
import warnings
from create_database import checkdb
import time
from prediction import predictor
from whatsapp_db import whatsappdb
from display_engagement import show_engagement
warnings.filterwarnings("ignore")
ps = PorterStemmer()
st.set_option('deprecation.showPyplotGlobalUse', False)


# ----- HEADING AND TITLE OF THE APP -----
design.heading_and_title()
design.add_logo()
design.sidebar_content()
checkdb().createdb()
checkdb().whatsappdb()
#  ----- DASHBOARD -----

#db = mysql.connector.connect(
#            host='mysqldb',
#            user='root',
#            passwd='password',
#            database='timestamp',
#            auth_plugin='mysql_native_password')
#query = "SELECT * FROM cleaned_data"
#df = pd.read_sql(query, con=db)
#word_df = visual_preprocessor().unique_word_count(df, 'reviews')
#destem_dict = {}
#for word in list(word_df['word']):
#    destem_dict[ps.stem(word)] = word
#rat_1, rat_2, rat_3 = visual_preprocessor().preprocess_data(df)


@st.cache_data
def load_data():
    rat_1 = pd.read_csv('rat_1.csv')
    rat_2 = pd.read_csv('rat_2.csv')
    rat_3 = pd.read_csv('rat_3.csv')
    new_df = pd.concat([rat_1, rat_2, rat_3])
    word_df = visual_preprocessor().unique_word_count(new_df, 'reviews_no_names')
    destem_dict = {}
    for word in list(word_df['word']):
        destem_dict[ps.stem(word)] = word
    positive_relevant = (rat_1.shape[0]/new_df.shape[0])*100
    neutral = (rat_2.shape[0]/new_df.shape[0])*100
    irrelevant = (rat_3.shape[0]/new_df.shape[0])*100
    return rat_1, rat_2, rat_3, destem_dict, positive_relevant, neutral, irrelevant
@st.cache_data
def cloud1(dict, df):
    visual_preprocessor().word_cloud(dict, df)
@st.cache_data
def cloud2(dict, df):
    visual_preprocessor().word_cloud(dict, df)
@st.cache_data
def cloud3(dict, df):
    visual_preprocessor().word_cloud(dict, df)

@st.cache_data
def pie_chart(positive, neutral, negative):
    st.markdown("<h4 style='text-align: center; color: white;'>Distribution of Reviews</h4>", unsafe_allow_html=True)
    labels = ['Positive', 'Neutral', 'Negative']
    values = [positive_relevant, neutral, irrelevant]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, 
                                marker={'colors':['rgb(115,183,167)', 'rgb(145,186,224)', 'rgb(215,78,91)']},
                                textfont=dict(size=20, family='calibri', color='white'))])
    fig.update_layout(width=450, height=450)
    st.plotly_chart(fig)

rat_1, rat_2, rat_3, destem_dict, positive_relevant, neutral, irrelevant = load_data()
# ----- interactive pie chart -----

col1, col2 = st.columns(2)
with col1:
    st.write('')
    pie_chart(positive_relevant, neutral, irrelevant) 

with col2:
    st.write('')
    st.write('')
    st.markdown("<h4 style='text-align: center; color: white;'>Positive</h4>", unsafe_allow_html=True)
    cloud1(destem_dict, rat_1)

col3, col4 = st.columns(2)
with col3:
    st.markdown("<h4 style='text-align: center; color: white;'>Neutral</h4>", unsafe_allow_html=True)
    cloud2(destem_dict, rat_2)

with col4:
    st.markdown("<h4 style='text-align: center; color: white;'>Negative</h4>", unsafe_allow_html=True)
    cloud3(destem_dict, rat_3)

st.markdown("---")
st.write('<div style="text-align:center"><h5><b>User Engagement In Whatsapp Groups</b></h5></div>', unsafe_allow_html=True)
col5, col6 = st.columns(2)
data = pd.read_csv('engagement_data.csv')
engagement = data.groupby(by='Username').count().sort_values(by='reviews', ascending=False).head(10).reset_index()[['Username', 'reviews']]
engagement['Engagement %'] = engagement.reviews.apply(lambda x: int(f'{(x/data.shape[0])*100:.0f}'))
with col5:
    total_messages = data.shape[0]
    st.write(total_messages)
    st.write('Top 10 Most Engaged Users')
    st.table(engagement)

with col6:
    st.write('')
    st.write('')
    user_list = list(engagement['Username']) + ['others']
    value_list = list(engagement['Engagement %']) + [round(abs(sum(engagement['Engagement %']) - 100), 2)]
    trace = go.Pie(labels=user_list, values=value_list, hole=.5, textfont=dict(color='rgb(15, 17, 22)', size=16, family='Arial'))
    layout = go.Layout(title=dict(text='Engagement % by User', x=0.5, y=1), width=500, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
    fig = go.Figure(data=[trace], layout=layout)
    st.plotly_chart(fig)

# ----- CUSTOM REVIEW SENTIMENT ANALYSIS -----

# ----- ANALYSIS ON initial DATA -----
st.markdown('<hr style="border-top: 3px solid #bbb;">', unsafe_allow_html=True)
    # ----- WHATSAPP CHAT FILE -> UPLOAD -----
val = False
with st.sidebar:
    st.info('Upload Whatsapp Chat File In TXT Format Below For Analysis')
    file = st.file_uploader("Choose a file", type=["txt"])
    if file:
        try:
            filename = file.name 
            data = file.read().decode("utf-8")     
            whatsapp_cleaner_intance = whatsapp_cleaner()
            cleaned_data = whatsapp_cleaner_intance.get_cleaned_whatsapp_data(data)
            try:
                cleaned_data.to_csv('cleaned_data.csv')
                val = True
            except:
                pass

        #except:
        except Exception as e:
            st.write(e)
           # st.write('OPERATION FAILED: PLEASE RELODE THE PAGE AND UPLOAD THE FILE AGAIN')
        try:
            csv = cleaned_data.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="cleaned_data.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)
        except:
            pass
                
    st.markdown('---')
    # ----- FACEBOOK SCRAPPING CODE -----
    time.sleep(1)
    st.info('Click Below To Scrap All Comments From Facebook')
    if st.button('Scrape Facebook Comments', key=1):
        scrapped_comments = FacebookScrapper().scrap_comments()
        if isinstance(scrapped_comments, pd.DataFrame):
            ins = whatsapp_cleaner()
            scrapped_comments['comments'] = scrapped_comments['comments'].apply(lambda x: ins.preprocessor(x))
            scrapped_comments.dropna(inplace = True)
            scrapped_comments = scrapped_comments.rename(columns={'comments':'reviews'})
            scrapped_comments['stemmed_reviews'] = scrapped_comments['reviews'].apply(lambda x: ins.stemming(x))
            scrapped_comments.dropna(inplace=True)
            scrapped_comments.to_csv('facebook_comments.csv')
            st.write('Comments scrapped successfully')
            try:
                fb_csv = scrapped_comments.to_csv(index=False)
                b64 = base64.b64encode(fb_csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="facebook_comments.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            except:
                pass
        else:
            dummy = pd.DataFrame({'reviews': [], 'stemmed_reviews': []})
            dummy.to_csv('facebook_comments.csv')
            st.write(scrapped_comments)
# ----- ANALYSE ON NEW DATA SCRIPT -----

    st.sidebar.markdown("---")
    st.info('Click Below For Analysis')
    if st.button('Perform Analysis On New Data', key=2):
        try:
            whatsapp = pd.read_csv('cleaned_data.csv')
            facebook = pd.read_csv('facebook_comments.csv')
            df = predictor().predict(whatsapp, facebook)
            destem_dict_new, rating1, rating2, rating3 = visual_preprocessor().preprocess_data(df)
            new_df = pd.concat([rating1, rating2, rating3])
            new_df.to_csv('df_labelled.csv')
            new_data_len = new_df.shape[0]
            pos = (rating1.shape[0]/new_data_len )*100
            neu = (rating2.shape[0]/new_data_len)*100
            irr = (rating3.shape[0]/new_data_len )*100
            try:
                new_df_csv = new_df.to_csv(index=False)
                b64 = base64.b64encode(new_df_csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="new_data_labelled.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)
            except:
                pass
        except Exception as e:
            st.write(e)
    st.write('')
    st.write('')


# ----- NEW DATA DASHBOARD -----
st.markdown('---')
@st.cache_data
def chart():
    visual_preprocessor().word_cloud(destem_dict_new, rating1)
@st.cache_data
def chart2():
    visual_preprocessor().word_cloud(destem_dict_new, rating2)
@st.cache_data
def chart3():
    visual_preprocessor().word_cloud(destem_dict_new, rating3)

try:
    if file:
        if pos:
            st.write('<div style="text-align:center"><h5><b>Analysis On New Data Using Supervised Machine Learning</b></h5></div>', unsafe_allow_html=True)
        else:
            pass
        col7, col8 = st.columns(2)
        with col7:
            st.write('')
            pie_chart(pos, neu, irr) 

        with col8:
            st.write('')
            st.write('')
            st.markdown("<h4 style='text-align: center; color: white;'>Positive</h4>", unsafe_allow_html=True)
            chart()

        col9, col10 = st.columns(2)
        with col9:
            st.markdown("<h4 style='text-align: center; color: white;'>Neutral</h4>", unsafe_allow_html=True)
            chart2()

        with col10:
            st.markdown("<h4 style='text-align: center; color: white;'>Negative</h4>", unsafe_allow_html=True)
            chart3()

        date = pd.to_datetime(whatsappdb().get_timestamp())
        cleaned_data2 = pd.read_csv('cleaned_data.csv')
        cleaned_data2['Date'] = pd.to_datetime(cleaned_data2['Date'])
        cleaned_data2 = cleaned_data2[cleaned_data2['Date']>date]

        col10, col11 = st.columns(2)
        if cleaned_data2.shape[0]>5:
            with col10:
                my_obj = show_engagement(cleaned_data2)
                my_obj.display_table()

            with col11:
                my_obj.display_chart()
                whatsappdb().update_timestamp(str(cleaned_data.sort_values(by='Date', ascending=False)['Date'].reset_index(drop=True)[0]).split(' ')[0])
        else:
            st.write('Data is not sufficient to show user engagement')
    else:
        pass
except Exception as e:
    pass

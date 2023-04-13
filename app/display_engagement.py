import streamlit as st
import plotly.graph_objects as go

class show_engagement():
    def __init__(self, df):
        self.df = df
        self.engagement = df.groupby(by='Username').count().sort_values(by='reviews', ascending=False).head(10).reset_index()[['Username', 'reviews']]
        self.engagement['Engagement %'] = self.engagement.reviews.apply(lambda x: int(f'{(x/df.shape[0])*100:.0f}'))
    def display_table(self):
        total_messages = self.df.shape[0]
        st.write(total_messages)
        st.write('Top 10 Most Engaged Users')
        st.table(self.engagement)
    def display_chart(self):
        st.write('')
        st.write('')
        user_list = list(self.engagement['Username']) + ['others']
        value_list = list(self.engagement['Engagement %']) + [round(abs(sum(self.engagement['Engagement %']) - 100), 2)]
        trace = go.Pie(labels=user_list, values=value_list, hole=.5, textfont=dict(color='rgb(15, 17, 22)', size=16, family='Arial'))
        layout = go.Layout(title=dict(text='Engagement % by User', x=0.5, y=1), width=500, height=500, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
        fig = go.Figure(data=[trace], layout=layout)
        st.plotly_chart(fig)

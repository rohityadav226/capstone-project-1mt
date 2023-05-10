import streamlit as st

class design():
    def heading_and_title():
        st.set_page_config(page_title="NAME REMOVED FOR PRIVACY CONCERNS", page_icon="📈", layout="wide")
        html_temp = """
            <div style="background-color:rgb(215,78,91);padding:10px">
            <h2 style="color:white;text-align:center;">Sentiment Analysis Dashboard</h2>
            </div>
            """
        st.markdown(html_temp,unsafe_allow_html=True)

    def add_logo():
        logo_url = 'URL REMOVED FOR PRIVACY CONCERNS'
        st.sidebar.image(logo_url, width=200)

    def sidebar_content():
        st.sidebar.header('Menu')

# if __name__=='__main__':
#     design()

import facebook as fb
import requests
import time
import traceback
import pandas as pd
import mysql.connector
import time
import datetime


class FacebookScrapper():
    def __init__(self):
        self.access_token = 'EAAxIqB6IPagBAGiKrToxsJE8CXZAIqh7IJPxQ8aqQfUM9ChY2YPQTZADVfG7P54EBOIH5T3BrFsJE329JWL0NbB9pgPZAS1QgSbS7EHPeSxY9ScWdXulrTE3TuD4ZArZCJnlLEReuQ66lp14ZBPvRRwLDrcE1it3hJUXV9Rj5AYMCjjdxAurBE'
        self.page_id = '1331516393589936' 
        self.db = mysql.connector.connect(
            host='mysqldb',
            user='root',
            passwd='password',
            database='timestamp',
            auth_plugin='mysql_native_password')
    
    def get_timestamp(self):
        mycursor = self.db.cursor()
        query = "SELECT time FROM facebooktimestamp WHERE datetime=(SELECT MAX(datetime) FROM facebooktimestamp)"
        mycursor.execute(query)
        timestamp_fetched = mycursor.fetchall()[0][0]
        return timestamp_fetched

    def update_timestamp(self, timestamp):
        mycursor = self.db.cursor()
        sql = "INSERT INTO facebooktimestamp(time) VALUES (%s)"
        mycursor.execute(sql,(timestamp,))
        self.db.commit()

    def extract_post_ids(self):
        facebook_timestamp = self.get_timestamp()
        dt = datetime.datetime.strptime(facebook_timestamp, '%Y-%m-%dT%H:%M:%S%z')
        timestamp = int(dt.timestamp())
        post_ids = []
        all_timestamps = []
        url = f'https://graph.facebook.com/v9.0/{self.page_id}/posts?access_token={self.access_token}&limit=1&since={timestamp}'
        while True:
            time.sleep(2)
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                all_timestamps.append(data['data'][0]['created_time'])
                post_ids.append(data['data'][0]['id'])
                if 'paging' in data and 'cursors' in data['paging'] and 'after' in data['paging']['cursors']:
                    url = f'https://graph.facebook.com/v9.0/{self.page_id}/posts?access_token={self.access_token}&limit=1&since={timestamp}'+'&after='+data['paging']['cursors']['after']
                else:
                    break
            except:
                break
        if all_timestamps:
            self.update_timestamp(all_timestamps[0])
        return post_ids

    def fetch_comments(self, post_ids):
        comment_data = []
        for post_id in post_ids:
            time.sleep(2)
            try:
                url = f'https://graph.facebook.com/v9.0/{post_id}/comments?access_token={self.access_token}'
                response = requests.get(url)
                response.raise_for_status()
                comments = response.json()
                comment_data.append(comments)
            except:
                break
        return comment_data

    def scrap_comments(self):
        post_ids = self.extract_post_ids()
        if post_ids:
            comment_data = self.fetch_comments(post_ids)
            fb_comments = []
            for dict in comment_data:
                try:
                    for inner_dict in dict['data']:
                        fb_comments.append(inner_dict['message'])
                except:
                    break
            fb_comments_df = pd.DataFrame(data={'comments': fb_comments})
            if fb_comments:
                return(fb_comments_df)
            else:
                self.db.close()
                return 'No comments available on fetched post'
        else:
            self.db.close()
            return 'No new comments available at the moment, please try again after few days'


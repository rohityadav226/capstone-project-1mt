import mysql.connector

class whatsappdb():
    def __init__(self):
        self.db = mysql.connector.connect(
            host='mysqldb',
            user='root',
            passwd='password',
            database='whatsapptimestamp',
            auth_plugin='mysql_native_password')

    def get_timestamp(self):
        mycursor = self.db.cursor()
        query = "SELECT date FROM whatsapptimestamp WHERE datetime=(SELECT MAX(datetime) FROM whatsapptimestamp)"
        mycursor.execute(query)
        timestamp_fetched = mycursor.fetchall()[0][0]
        return timestamp_fetched

    def update_timestamp(self, timestamp):
        mycursor = self.db.cursor()
        sql = "INSERT IGNORE INTO whatsapptimestamp(date) VALUES (%s)"
        mycursor.execute(sql,(timestamp,))
        self.db.commit()

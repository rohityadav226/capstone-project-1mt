import mysql.connector

class checkdb():
    def __init__(self):
        pass
    def createdb(self):
        mydb = mysql.connector.connect(host="mysqldb", user="root", password="password")
        mycursor = mydb.cursor()
        mycursor.execute("CREATE DATABASE IF NOT EXISTS timestamp;")
        mycursor.execute("CREATE DATABASE IF NOT EXISTS whatsapptimestamp;")
        mydb.commit()
        mydb.close()
        mydb = mysql.connector.connect(host="mysqldb", user="root", password="password", database="timestamp")
        mycursor = mydb.cursor()
        mycursor.execute("CREATE TABLE IF NOT EXISTS facebooktimestamp (datetime DATETIME PRIMARY KEY DEFAULT CURRENT_TIMESTAMP, time VARCHAR(50))")
        query = "SELECT * FROM facebooktimestamp WHERE time = %s"
        mycursor.execute(query, ('2023-02-06T02:52:43+0000',))
        results = mycursor.fetchall()
        if len(results) > 0:
            mydb.commit()
            mydb.close()
        else:
            query = "INSERT INTO facebooktimestamp(time) VALUES (%s)"
            values = ('2023-02-06T02:52:43+0000',)
            mycursor.execute(query, values)
            mydb.commit()
            mydb.close()

    def whatsappdb(self):
        mydb = mysql.connector.connect(host="mysqldb", user="root", password="password")
        mycursor = mydb.cursor() 
        mycursor.execute("CREATE DATABASE IF NOT EXISTS whatsapptimestamp;")
        mydb.commit()
        mydb.close()
        mydb = mysql.connector.connect(host="mysqldb", user="root", password="password", database="whatsapptimestamp")
        mycursor = mydb.cursor()
        mycursor.execute("CREATE TABLE IF NOT EXISTS whatsapptimestamp (datetime DATETIME PRIMARY KEY DEFAULT CURRENT_TIMESTAMP, date VARCHAR(50))")
        query = "SELECT * FROM whatsapptimestamp WHERE date = %s"
        mycursor.execute(query, ('2023-01-25',))
        results = mycursor.fetchall()
        if len(results) > 0:
            mydb.commit()
            mydb.close()
        else:
            query = "INSERT INTO whatsapptimestamp(date) VALUES (%s)"
            values = ('2023-01-25',)
            mycursor.execute(query, values)
            mydb.commit()
            mydb.close()


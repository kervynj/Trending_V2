import csv
import MySQLdb
class database_interface():


    def __init__(self):

        self.db = MySQLdb.connect(host="127.0.0.1",port =3306,user="root",passwd="",db="test")

        self.cursor = self.db.cursor()


    def query_handler(self,query):

        try:
            self.cursor.execute(query)
            self.db.commit()

        except MySQLdb.Error:
            self.db.rollback()
            raise

    def db_fetch(self,query):

        results = []

        try:
            self.cursor.execute(query)
            results= self.cursor.fetchall()
            return results
        except MySQLdb.Error as e:
            print e
            self.db.rollback()
            raise


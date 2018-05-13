import sqlite3


class SQLiteHelper():
    def __init__(self, db):
        self.db = db

    def connect(self):
        self.conn = sqlite3.connect(self.db)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

    def query(self, sql, params=()):
        self.connect()
        try:
            self.cursor.execute(sql, params)
            ret = self.cursor.fetchall()
            return ret
        except:
            pass
        finally:
            self.close()

    def execute(self, sql, params=()):
        self.connect()
        try:
            self.cursor.execute(sql, params)
            print('rowcount: {}'.format(self.cursor.rowcount))
            self.conn.commit()
        except:
            pass
        finally:
            self.close()


if __name__ == '__main__':
    s = SQLiteHelper('dev_data.sqlite')
    ret= s.query("select id,body_html from blogs where body_html is not null")
    if ret:
        for tup in ret:
            print(tup)
    s.execute("update blogs set body_html='' where id=406")

    
        

 

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

    def cud(self, sql, params=()):
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
    for tup in s.query("select id, username, email from users"):
        print(tup)
    s.cud("delete from users where id=23")

 

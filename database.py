from psycopg2 import connect


class Database:
    def __init__(self, host="'localhost'", dbname="'Publication Management System'", user="'postgres'",
                 password="'113113113'"):
        conn_string = " host=" + host + " dbname=" + dbname + " user=" + user + " password=" + password
        print("Connecting to database -> %s" % (conn_string))

        self.connection = connect(conn_string)
        self.cursor = self.connection.cursor()
        print("Connected!")

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
        self.cursos.close()


class Table:
    def __init__(self, name, database):
        self.name = name
        self.db = database
        self.search = 'Search by title'

    def query(self, query, data=None):
        query = self.db.cursor.mogrify(query, data)
        # print("!" + query + "!")
        # try:
        self.db.cursor.execute(query)
        self.db.commit()
        # except Exception as e:
        #     print(e.pgerror)

    def giveAnswers(self):
        records = self.db.cursor.fetchall()
        # pprint.pprint(records)
        return records

    def showAll(self):
        # cursor = self.db.cursor
        self.query("select * from " + self.name)
        return self.giveAnswers()

    def showFromMask(self, mask):
        # cursor = self.db.cursor
        s = ''
        for m in mask:
            s += m + ","
        s = s[:(len(s) - 1)]
        query = "select " + s + " from " + self.name
        print(query)
        return query
        # self.query(query)
        # answer = self.giveAnswers()
        # print(answer)
        # return answer

    def searchByTitle(self, mask):
        s = ''
        for m in mask:
            s += m + ","
        s = s[:(len(s) - 1)]

        # query = """select " + s + " from " + self.name + " where title like any '%""" + " %s " + """%' """
        # self.search = [self.search]
        # print query
        # self.db.cursor.execute(query, self.search)
        query = "select " + s + " from " + self.name + " where title like '%" + self.search + "%' "
        print(query)
        return query
        # self.db.cursor.execute(query)
        # self.db.commit()
        #
        # return self.giveAnswers()

    def delete(self):
        self.query("drop table " + self.name)

    def clear(self):
        self.query('truncate table ' + self.name + " cascade")

    def insertValues(self, dict={"": "''"}):
        query = "insert into " + self.name + "("
        keys = dict.keys()
        values = dict.values()
        # print(keys)

        for i in xrange(len(keys) - 1):
            query += str(keys[i]) + ", "
        query += str(keys[len(keys) - 1]) + ") values ("
        for i in xrange(len(values) - 1):
            query += "%s,"
        query += "%s);"
        # print("inserting values")
        self.query(query, dict.values())
        # print(self.db.cursor.mogrify(query, dict.values()))
        # self.db.cursor.execute(query, dict.values())
        # self.db.commit()

    def count(self):
        self.query("select count(*) from "+self.name)
        return self.giveAnswers()[0][0]

if __name__ == '__main__':
    pass
    # db = Database()
    # author = Table("publications", db)
    # print(author.showAll())

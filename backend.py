import os
from database import *
import tornado.ioloop
import tornado.web
import hashlib


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user")

    def HTML(self, fileName, kwargs=None):
        if kwargs is not None:
            return self.render("frontend\\html\\" + fileName + ".html", **kwargs)
        else:
            return self.render("frontend\\html\\" + fileName + ".html")

    def hash(self, string):
        return hashlib.sha224(string).hexdigest()


class MainHandler(BaseHandler):
    def get(self):
        self.HTML("index")


class LoginHandler(BaseHandler):
    def get(self):
        # self.write(HTML("login"))
        # self.static_url("login.html")
        if self.get_current_user() is not None:
            self.redirect("/table")
        else:
            self.HTML("login")

    def post(self, *args, **kwargs):
        print("entered pass !" + self.get_argument("password") + "!")
        query = "SELECT * FROM checking('" + str(self.get_argument("login")) + "','" + self.hash(
            self.get_argument("password")) + "')"
        users.query(query)
        answer = users.giveAnswers()[0][0]
        if answer is not None:
            self.set_secure_cookie("user", self.get_argument("login"))
            self.redirect("/table")
        else:
            self.redirect("/")


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("user")
        self.redirect("/")


class RegistrationHandler(BaseHandler):
    def get(self):
        if self.get_current_user() is not None:
            self.redirect("/login")
        else:
            self.HTML("registration")
            print(self.get_current_user())

    def post(self):
        password1 = self.get_arguments("password1")[0]
        password2 = self.get_arguments("password2")[0]
        print("pass1 " + password1 + " pass2 " + password2)
        if not ((password1 != password2) | (password1 == '')):
            users.insertValues({'login': self.get_argument("login"), "pass_hash": self.hash(password1)})
        self.redirect("/")


class GraphicHandler(BaseHandler):
    def get(self):
        self.HTML("graphics",
                  dict(username=self.get_current_user(), books_count=books.count(), article_count=articles.count(),
                       conf_count=conf_reports.count()))


class PreviousHandler(BaseHandler):
    def get(self):
        global page
        if page > 1:
            page -= 1
        self.redirect("/table")


class NextHandler(BaseHandler):
    def get(self):
        global page
        page += 1
        self.redirect("/table")


class SortingHandler(BaseHandler):
    def get(self):
        global query
        query = "(" + query + ") order by year desc"
        self.redirect("/table")


class TableHandler(BaseHandler):
    def __init__(self, application, request, **kwargs):
        super(TableHandler, self).__init__(application, request, **kwargs)
        self.domain = ('title', 'year', 'doi', 'abstract')

    @tornado.web.authenticated
    def get(self):
        global table, page, query
        print "in get" + publication.search
        # print("page", page)
        perPage = 10
        print(query)

        return self.HTML("tables", {'username': self.get_current_user(),
                                    'domains': self.domain,
                                    'publications': create_table(query, page, perPage, self.domain),
                                    'search': publication.search, 'amount': publication.count()})

    def post(self):
        global table, page, query
        print('post query')
        key_list = ('title', 'doi', 'year', 'author_name', 'volume', 'issn', 'journal_name', 'query')
        searched = dict()

        for key in key_list:
            searched[key] = ''

        isEmpty = True
        for key in key_list:
            searched[key] = self.get_argument(key)
            if searched[key] != '':
                isEmpty = False
        print(searched)
        print('IsEmpty:', isEmpty)

        publication.search = searched['query']
        if publication.search != '' and publication.search != "Search by title":
            query = publication.searchByTitle(self.domain)
            publication.search = 'Search by title'
        else:
            print("extended search")
            if isEmpty:
                query = publication.showFromMask(self.domain)
                publication.search = 'Search by title'
            else:
                query = self.extended_search(searched, self.domain)
        self.redirect("/table")

    def extended_search(self, searchby, domains):
        ch = ''
        searched = dict()
        key_list = ('title', 'doi', 'year', 'author_name', 'volume', 'issn', 'journal_name')
        for key in key_list:
            searched[key] = ch

        for i in xrange(len(searchby)):
            if searched.get(searchby.keys()[i]) == ch:
                searched[searchby.keys()[i]] = searchby.values()[i]

        in_query = [add_where(dict(title=searched['title'], year=searched['year'], doi=searched['doi']), ch),
                    add_where(dict(author_name=searched['author_name']), ch),
                    add_where(dict(volume=searched['volume']), ch),
                    add_where(dict(issn=searched['issn'], name=searched['journal_name']), ch)]

        select = ''
        for key in domains:
            select += key + ","
        select = select[:len(select) - 1]

        query = '''select ''' + select + ''' from
        (((
            (
                ( select * from publications ''' + in_query[0][0] + ''' ) as p
                      join
                          (select * from created_by) as cb on p.id=cb.publication_id)
                               join
                               (select * from authors aut ''' + in_query[1][0] + """ ) as a on cb.author_id=a.id)
                                join

                                (select * from articles art """ + in_query[2][0] + """ ) as ar on ar.publication_id=p.id)
                                    join
                                    (select * from journals jou """ + in_query[3][
            0] + """ ) as j on j.id=ar.journal_id)"""

        for i in xrange(1, 4):
            in_query[0][1] = in_query[0][1] + in_query[i][1]

        query = db.cursor.mogrify(query, in_query[0][1])
        # print(query)
        return query
        # books.query(query, [searched[key] for key in key_list])
        #
        # # print(len(books.giveAnswers()))
        # return books.giveAnswers()


def add_where(param, ch):
    answer = ""
    values = []
    flag = False
    for i in xrange(len(param)):
        if param.values()[i] != ch:
            if not flag:
                answer += 'where '
            answer += param.keys()[i] + "=%s "
            values.append(param.values()[i])

    return [answer, values]


def create_table(query, page, perPage, domains):
    print('page', page)
    dom = ""
    for d in domains:
        dom += d + ","
    dom = dom[:len(dom) - 1]
    q = "select * from (" + query + ") as a  limit " + str(perPage) + " offset " + str(
        (page - 1) * perPage)
    print(q)
    books.query(q, None)
    global table
    return books.giveAnswers()


settings = {

    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "static_path": os.path.join(os.path.dirname(__file__), 'frontend/')

}

application = tornado.web.Application([
    (r"/", MainHandler), (r"/login", LoginHandler), (r"/logout", LogoutHandler),
    ("/registration", RegistrationHandler),
    (r"/table", TableHandler), ("/graphic", GraphicHandler), ("/previous", PreviousHandler), ("/next", NextHandler),
    ("/sortbyyear", SortingHandler)],
    **settings)

if __name__ == "__main__":
    db = Database()
    users = Table("users", db)
    publication = Table("publications", db)
    doc_type = Table("doc_type", db)
    institutions = Table("institutions", db)
    keywords = Table("keywords", db)
    has = Table("has", db)
    authors = Table('authors', db)
    created_by = Table('created_by', db)
    publishers = Table('publishers', db)
    books = Table('books', db)
    journals = Table('journals', db)
    articles = Table('articles', db)
    conferences = Table('conferences', db)
    conf_reports = Table('conf_reports', db)

    global table, page, query
    query = publication.showFromMask(('title', 'year', 'doi', 'abstract'))

    # table = publication.showFromMask(('title', 'year', 'doi', 'abstract'))
    page = 1
    # print(extended_search(dict(year=2000)))
    # books.query("select * from books")
    # print(db.cursor.fetchone())
    # books.query("select * from books")
    # print(db.cursor.fetchone())

    application.listen(8000)
    tornado.ioloop.IOLoop.current().start()

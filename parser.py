import HTMLParser
from lxml import etree
from __builtin__ import file
from database import *
import random


class Parsing:
    def __init__(self, numberOfXMLFile):  # one file must contain one XML record
        # f = open("xmls from ieee by year\\" + str(numberOfXMLFile) + ".xml", 'r')  # file with xml
        # parser = etree.XMLParser(attribute_defaults=True, strip_cdata=False)  # parser
        # tree = etree.parse(f, parser=parser)  # creating tree
        # count = int(tree.xpath('/root/totalfound')[0].text)

        for i in xrange(1000):
            print(i)
            self.query = {}
            self.result = {}
            self.availableList = (
                'title', 'authors', 'affiliations', 'term', 'pubtitle', 'punumber', 'pubtype', 'publisher', 'volume',
                'issue',
                'py', 'spage', 'epage', 'abstract', 'issn', 'isbn', 'arnumber', 'doi', 'publicationId', 'mdurl', 'pdf')
            self.data = dict()

            for tag in self.availableList:
                self.data[tag] = []

            # creating tree
            self.tree = self.createTree(numberOfXMLFile, i)
            if self.tree is not None:
                self.create_data_from_tree(self.tree)

                # author processing
                if len(self.data['authors']) != 0:
                    # print('yes')
                    self.data['authors'] = self.author_processing(self.data['authors'][0].split(';'))

                for key in self.data:
                    if self.data[key] == []:
                        self.data[key] = [' ']

                self.data['volume'] = map(int2, self.data['volume'])
                self.data['spage'] = map(int2, self.data['spage'])
                self.data['epage'] = map(int2, self.data['epage'])
                self.data['py'] = map(int2, self.data['py'])
                self.data['publicationId'] = map(int2, self.data['publicationId'])

                # print(self.data)
                self.Filler(self.data)
                # self.depthParsing(node)

    def depthParsing(self, node):
        # print(node.tag, self.query)
        i = 0
        for n in node:
            self.depthParsing(n)
            i += 1

        if i == 0:
            if self.d.__contains__(node.tag):
                if self.list.__contains__(self.d[node.tag]):
                    self.query[self.d[node.tag]] = HTMLParser.HTMLParser().unescape(node.text).encode("utf-8")
        else:
            # print(self.query)
            if self.query != dict():
                self.result.update(self.query)
                self.query = {}

    def createTree(self, XMLFileNumber, documentNumber):
        try:
            f = open("xmls from ieee by year\\" + str(XMLFileNumber) + ".xml", 'r')  # file with xml
            parser = etree.XMLParser(attribute_defaults=True, strip_cdata=False)  # parser
            tree = etree.parse(f, parser=parser)  # creating tree
            articleTree = tree.xpath('/root/document')[documentNumber]
            return articleTree
        except:
            return None

    def create_data_from_tree(self, node):
        i = 0
        for n in node:
            i += 1
            self.create_data_from_tree(n)

        if i == 0:
            if self.availableList.__contains__(node.tag):
                self.data[node.tag].append(HTMLParser.HTMLParser().unescape(node.text).encode("utf-8"))

    def author_processing(self, authors):  # deleting spaces
        for k in xrange(len(authors)):
            author = authors[k]
            if len(author) == 0:
                continue
            i = 0
            while author[i] == ' ':
                i += 1
                if i == len(author):
                    break

            j = len(author) - 1
            while author[j] == ' ' and j > 0:
                j -= 1
                if j == 0:
                    break

            authors[k] = author[i:j]
        return authors

    class Filler:
        def __init__(self, data):
            self.data = data
            self.max_randint = 10 ** 7

            self.doc_type_id = []
            self.institutions_id = []
            self.publication_id = []
            self.keywords_id = []
            self.authors_id = []
            self.publisher_id = []
            self.journals_id = []
            self.conferences_id = []

            # institutions.clear()
            # doc_type.clear()
            # publications.clear()
            # keywords.clear()

            # methods
            self.fill_institution()
            self.fill_doc_type()

            self.fill_publications()

            self.fill_keywords()
            self.fill_has()

            self.fill_authors()
            self.fill_created_by()

            # try:
            if self.data['pubtype'][0] == 'Books & eBooks':
                self.fill_books()

            if self.data['pubtype'][0] == 'Journals & Magazines':
                self.fill_articles()

            if self.data['pubtype'][0] == 'Conference Publications':
                self.fill_conference_reports()

            if self.data['pubtype'][0] == 'Early Access Articles':
                self.fill_articles()

            if self.data['pubtype'][0] == 'Standards':
                self.fill_articles()
                #
                # except:
                #     pass

                # print(self.doc_type_id)
                # print(self.authors_id)
                # print(self.publication_id)
                # print(self.journals_id)

        def fill_doc_type(self):
            # try
            doc_type.showAll()
            type = self.first(self.data['pubtype'])
            id = random.randint(0, self.max_randint)
            # print(id, type)

            res_id = self.is_putted_in_db(doc_type, dict(name=type))
            if res_id is None:
                while self.is_putted_in_db(doc_type, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                doc_type.insertValues(dict(id=id, name=type))
                self.doc_type_id.append(id)
            else:
                self.doc_type_id.append(res_id)
                # except:
                #     print("error in doc_type")

        def fill_institution(self):
            for institute in self.data['affiliations']:
                # try:
                id = random.randint(0, self.max_randint)
                # print(id, institute)

                res_id = self.is_putted_in_db(institutions, dict(name=institute))
                if res_id is None:
                    while self.is_putted_in_db(institutions, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                    institutions.insertValues(dict(id=id, name=institute))
                    self.institutions_id.append(id)
                else:
                    self.institutions_id.append(res_id)
                    # except:
                    #     print("error in institution")

        def fill_publications(self):  # while inserting one record
            # try:
            id = self.first(self.data['publicationId'])
            title = self.first(self.data['title'])
            year = self.first(self.data['py'])
            doi = self.first(self.data['doi'])
            abstract = self.first(self.data['abstract'])
            institutionid = self.first(self.institutions_id)
            # print(id, institute)
            for doc_typeid in self.doc_type_id:
                values = dict(title=title, year=year, doi=doi, abstract=abstract, doc_type_id=doc_typeid,
                              institution_id=institutionid)

                # print(values)
                res_id = self.is_putted_in_db(publications, values)

                # print(res_id)
                if res_id is None:
                    while self.is_putted_in_db(publications, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                    values['id'] = id
                    publications.insertValues(values)
                    self.publication_id.append(id)
                else:
                    self.publication_id.append(res_id)
                    # except:
                    #     print("error in publications")

        def fill_keywords(self):
            for term in self.data['term']:
                # try:
                values = dict(title=term)
                # print(values)
                id = random.randint(0, self.max_randint)
                res_id = self.is_putted_in_db(keywords, values)
                if res_id is None:
                    while self.is_putted_in_db(keywords, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                    values['id'] = id
                    keywords.insertValues(values)
                    self.keywords_id.append(id)
                else:
                    self.keywords_id.append(res_id)

                    # except:
                    #     print("error in keywords")

        def fill_has(self):
            # try:
            for keywordid in self.keywords_id:
                for publicationid in self.publication_id:
                    values = dict(publication_id=publicationid, keyword_id=keywordid)
                    query = "select * from has where publication_id=%s and keyword_id=%s;"
                    has.query(query, values.values())
                    # print(authors.giveAnswers())
                    if len(has.giveAnswers()) == 0:
                        has.insertValues(values)

                        # print(values)
                        # except:
                        #     print("error in has")

        def fill_authors(self):
            for author in self.data['authors']:
                # try:
                id = random.randint(0, self.max_randint)
                values = dict(name=author)
                # print(values)

                res_id = self.is_putted_in_db(authors, values)
                if res_id is None:
                    while self.is_putted_in_db(authors, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                    values['id'] = id
                    authors.insertValues(values)
                    self.authors_id.append(id)
                else:
                    self.authors_id.append(res_id)

                    # except:
                    #     print("error in authors")

        def fill_created_by(self):
            # try:
            for authorid in self.authors_id:
                for publicationid in self.publication_id:
                    values = dict(publication_id=publicationid, author_id=authorid)
                    query = "select * from created_by where publication_id=%s and author_id=%s;"
                    created_by.query(query, values.values())
                    # print(authors.giveAnswers())
                    if len(created_by.giveAnswers()) == 0:
                        created_by.insertValues(values)

                        # print(values)
                        # except:
                        #     print("error in created_by")

        def fill_articles(self):
            self.fill_journals()
            # try:
            for journalsid in self.journals_id:
                for publicationid in self.publication_id:
                    values = dict(publication_id=publicationid, journal_id=journalsid, volume=self.data['volume'][0],
                                  start_page=self.data['spage'][0], last_page=self.data['epage'][0])
                    query = "select * from articles where publication_id=%s;"
                    articles.query(query, [publicationid])
                    # print(authors.giveAnswers())
                    if len(articles.giveAnswers()) == 0:
                        articles.insertValues(values)
                        # print(values)
                        # except:
                        #     print("error in articles")

        def fill_journals(self):
            publisher = self.first(self.data['pubtitle'])
            issn = self.first(self.data['issn'])
            # try:
            id = random.randint(0, self.max_randint)
            values = dict(name=publisher, issn=issn)
            # print(values)

            res_id = self.is_putted_in_db(journals, values)
            # print(res_id)
            if res_id is None:
                while self.is_putted_in_db(keywords, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                values['id'] = id
                journals.insertValues(values)
                self.journals_id.append(id)
            else:
                self.journals_id.append(res_id)

                # except:
                #     print("error in journals")

        def fill_conference_reports(self):
            self.fill_conferences()
            # try:
            for conferenceid in self.conferences_id:
                for publicationid in self.publication_id:
                    values = dict(publication_id=publicationid, conference_id=conferenceid,
                                  volume=self.data['volume'][0],
                                  start_page=self.data['spage'][0], last_page=self.data['epage'][0])
                    query = "select * from conf_reports where publication_id=%s and conference_id=%s;"
                    conf_reports.query(query, [publicationid, conferenceid])
                    # print(authors.giveAnswers())
                    if len(conf_reports.giveAnswers()) == 0:
                        conf_reports.insertValues(values)
                        # print(values)
                        # except:
                        #     print("error in has")

        def fill_conferences(self):
            conference = self.first(self.data['pubtitle'])
            # try:
            id = random.randint(0, self.max_randint)
            values = dict(name=conference)
            # print(values)

            res_id = self.is_putted_in_db(conferences, values)
            # print(res_id)
            if res_id is None:
                while self.is_putted_in_db(keywords, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                values['id'] = id
                conferences.insertValues(values)
                self.conferences_id.append(id)
            else:
                self.conferences_id.append(res_id)

                # except:
                #     print("error in journals")

        def fill_books(self):
            self.fill_publisher()
            # try:
            for publisherid in self.publisher_id:
                for publicationid in self.publication_id:
                    values = dict(publication_id=publicationid, publisher_id=publisherid, isbn=self.data['isbn'][0],
                                  start_page=self.data['spage'][0], last_page=self.data['epage'][0])
                    query = "select * from books where publication_id=%s and publisher_id=%s;"
                    books.query(query, [publicationid, publisherid])
                    # print(authors.giveAnswers())
                    if len(books.giveAnswers()) == 0:
                        books.insertValues(values)
                        # print(values)
                        # except:
                        #     print("error in has")

        def fill_publisher(self):
            for publisher in self.data['publisher']:
                # try:
                id = random.randint(0, self.max_randint)
                values = dict(name=publisher)
                # print(values)

                res_id = self.is_putted_in_db(publishers, values)
                if res_id is None:
                    while self.is_putted_in_db(keywords, dict(id=id)) is not None:
                        id = random.randint(0, self.max_randint)
                    values['id'] = id
                    publishers.insertValues(values)
                    self.publisher_id.append(id)
                else:
                    self.publisher_id.append(res_id)

                    # except:
                    #     print("error in publishers")

        def is_putted_in_db(self, table, data):
            query = "select id from " + table.name + " where "
            keys = data.keys()
            values = data.values()
            values_for_search = []
            for i in xrange(len(keys)):
                if data.values()[i] is not None:
                    query += keys[i] + "=%s and "
                    values_for_search.append(values[i])

            if query[len(query) - 4:len(query)] == 'and ':
                query = query[:len(query) - 4]
            # print(query)
            table.query(query, values_for_search)
            answers = table.giveAnswers()
            # print(answers)
            return None if len(answers) == 0 else answers[0][0]

        def first(self, array):
            return None if len(array) == 0 else array[0]


def int2(a):
    b = 0
    try:
        b = int(a)
    except:
        pass
    return b


class Slicer:  # divide huge xml file on many small xml files
    def __init__(self, fileName, maxCountInFile, keyword):
        inputFile = file(fileName, 'r')
        fileCount = 0

        keyword2 = '<' + keyword
        keyword = '</' + keyword + '>'
        current = ''
        while (current[:len(keyword2)] != keyword2):
            current = inputFile.readline()

        while (current != '<\dblp>' and fileCount <= 1000):
            toFile = current
            articleCount = 0
            while (articleCount < maxCountInFile):
                current = ''
                while (current[:len(keyword)] != keyword):
                    current = inputFile.readline()
                    toFile += current
                articleCount += 1

            current = ''
            f = file('xmls\\' + str(fileCount) + '.xml', 'w')
            fileCount += 1
            print(fileCount)
            f.write(
                """<?xml version="1.0" encoding="ISO-8859-1"?> \n <!DOCTYPE dblp SYSTEM "dblp.dtd"> \n<dblp>\n""" + toFile + "</dblp>")
            f.close()

        f = file('xmls\\' + str(fileCount) + '.xml', 'w')
        fileCount += 1
        f.write(toFile + "</dblp>")
        f.close()


if __name__ == '__main__':
    # Slicer('dblp.xml', 1000, 'article')

    db = Database()
    publications = Table("publications", db)
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

    # parsing = Parsing(1)
    for i in xrange(800,932):
        print('xmls '+str(i))
        parsing = Parsing(i)


    # for i in xrange(1000, 1100):
    #     f = open("xmls from ieee\\" + str(i) + ".xml", 'r')
    #     parser = etree.XMLParser(attribute_defaults=True, strip_cdata=False)  # , dtd_validation=True, load_dtd=True)
    #
    #     try:
    #         tree = etree.parse(f, parser=parser)
    #         dblp = tree.xpath('/root/document')
    #     except:
    #         pass

    # for article in dblp:
    #     parse = Parsing(article, domainList)
    #     result = parse.result
    #     pub.insertValues(result)
    # print(result)
    # print() #after that we must do print(.decode("utf-8))

    # print(dblp)
    #
    # # print(parse.result)
    # for d in parse.result:
    #     if (d['title'] != None):
    #         author.insertValues(d)
    #
    #     try:
    #         pass
    #     except:
    #         print(d)




    # title = open("titles.txt", 'r')
    # for i in xrange(1):
    #     print(title.readline())
    # title.close()

    # parser = etree.XMLParser()#attribute_defaults=True, dtd_validation=True, load_dtd=True)
    # tree = etree.parse(open("xmls\\0.xml", 'r'), parser=parser)
    # print(etree.tostring(tree.getroot()))

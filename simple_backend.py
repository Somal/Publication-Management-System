import os
import tornado.ioloop
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        items = [["Item 1", "Item 2", "Item 3"], ["1", "2", "3","ololo"]]

        return self.render("template.html", title="My title", items=items)


settings = {
    "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    "login_url": "/login",
    "static_path": os.path.join(os.path.dirname(__file__), 'frontend/')
}

application = tornado.web.Application([
    (r"/", MainHandler)
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()

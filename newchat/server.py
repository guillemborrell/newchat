import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
from tornado.options import define, options
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, Integer, String
import datetime
import os
import json

js_folder = os.path.join(os.path.dirname(__file__), 'js')
define("db", default="sqlite://", help="SQLAlchemy engine connection string")
engine = create_engine(options.db)
Base = declarative_base()
Session = sessionmaker(bind=engine)
sess = Session()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    when = Column(String)
    name = Column(String)
    message = Column(String)

    def json(self):
        return json.dumps({'when': self.when,
                           'name': self.name,
                           'message': self.message})

Base.metadata.create_all(engine)
    
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        loader = tornado.template.Loader(os.curdir)
        messages = sess.query(
            Message).order_by(
                Message.id.desc()).limit(10).all()
        self.write(loader.load("home.html").generate(messages=messages))

        
class ChatWebSocket(tornado.websocket.WebSocketHandler):
    connections = set()
    def open(self):
        self.connections.add(self)
        print("WebSocket opened")

    def on_message(self, message):
        data = json.loads(message)
        data['when'] = datetime.datetime.now().strftime("%d/%m %H:%M")
        m = Message(**data)
        sess.add(m)
        sess.commit()
        [conn.write_message(json.dumps(data)) for conn in self.connections]

    def on_close(self):
        self.connections.remove(self)
        print("Websocket closed")

        
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/chat", ChatWebSocket),
        (r"/js/(.*)", tornado.web.StaticFileHandler, {'path': js_folder}),
    ], debug=True)

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

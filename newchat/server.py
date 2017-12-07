import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.template
from tornado.options import define, options
from sqlalchemy import create_engine, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy import Column, Integer, String
from matplotlib import mathtext
from io import StringIO
import datetime
import os
import json
import html
import re

js_folder = os.path.join(os.path.dirname(__file__), 'js')
html_folder = os.path.join(os.path.dirname(__file__), 'html')
css_folder = os.path.join(os.path.dirname(__file__), 'css')

define("db", default="sqlite://", help="SQLAlchemy engine connection string")
define("port", default="8888", help="HTTP server port")
options.parse_command_line()
engine = create_engine(options.db)

Base = declarative_base()
Session = sessionmaker(bind=engine)
sess = Session()

# global font properties for math
try:
    font_properties = mathtext.FontProperties()
    font_properties.set_size(12)
except NameError:
    pass

# global regexp
regexp_latex = re.compile("\\$.*?(?<!\\\\)\\$")


def parse_math(message):
    equations = regexp_latex.findall(message)

    replacements = list()
    for eq in equations:
        output = StringIO()
        try:
            mathtext.math_to_image(eq,
                                   output,
                                   dpi=72,
                                   prop=font_properties,
                                   format='svg')
            svg_equation = ''.join(output.getvalue().split('\n')[4:])
            replacements.append(svg_equation)

        except ValueError:
            replacements.append('<i>Error in equation</i>')

        output.close()

    newmessage = regexp_latex.sub('{}', message)

    try:
        newmessage = newmessage.format(*replacements)
    except:
        newmessage = 'Could not understand your message'

    return newmessage


def prettify(message):
    image_formats = ['.png', '.gif', '.jpg', '.jpeg']
    video_formats = ['.mp4', '.ogg', '.webm']
    youtube_urls = ['youtube.com', 'youtu.be']
    urls = ['http://', 'https://']
    newmessage = list()

    message = parse_math(message)

    for w in message.split():
        if any([fmt in w for fmt in video_formats]):
            newmessage.append(
                u'<video class="img-responsive" controls><source src="{}" type="video/webm"></video>'.format(w)
            )
        elif any([fmt in w for fmt in youtube_urls]):
            newmessage.append(
                u'<iframe width="480" height="320" src="//www.youtube.com/embed/{}" frameborder="0" allowfullscreen></iframe>'.format(w[-11:])
            )
        elif any([fmt in w for fmt in image_formats]):
            newmessage.append(
                u'<a href="{}" target="_blank"><img src="{}" class="img-responsive"></a>'.format(w,w)
            )
        elif any([fmt in w for fmt in urls]):
            newmessage.append(
                u'<a href="{}" target="_blank">{}...</a>'.format(w,w[:20])
            )
        else:
            newmessage.append(w)

    return ' '.join(newmessage)


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    when = Column(String)
    name = Column(String)
    message = Column(String)
    chat = Column(String)

    def to_dict(self):
        return {'when': self.when,
                'name': self.name,
                'message': self.message}


Base.metadata.create_all(engine)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        chat = self.get_argument("chat", "root")
        loader = tornado.template.Loader(html_folder)
        messages = sess.query(
            Message).filter(
                Message.chat == chat).order_by(
                    Message.id.desc()).limit(20).all()
        if messages:
            last = messages[-1].id
        else:
            last = 1
        self.write(loader.load("home.html").generate(messages=messages,
                                                     last=last,
                                                     chat=chat))


class PreviousMessagesHandler(tornado.web.RequestHandler):
    def get(self):
        fr = self.get_argument('from')
        chat = self.get_argument('chat', 'root')
        messages = sess.query(
            Message).filter(
                and_(Message.id < fr, Message.chat == chat)).order_by(
                    Message.id.desc()).limit(10).all()
        if messages:
            last = messages[-1].id
        else:
            last = 1
        self.write(json.dumps({'messages': [m.to_dict() for m in messages],
                               'last': last}))

        
class ChatWebSocket(tornado.websocket.WebSocketHandler):
    connections = set()
    # def check_origin(self, origin):
    #     return True
    
    def open(self):
        self.connections.add(self)

    def on_message(self, message):
        data = json.loads(message)
        data['when'] = datetime.datetime.now().strftime("%d/%m %H:%M")
        data['message'] = html.escape(data['message'], quote=False)
        data['message'] = prettify(data['message'])
        m = Message(**data)
        sess.add(m)
        sess.commit()
        [conn.write_message(json.dumps(data)) for conn in self.connections]

    def on_close(self):
        self.connections.remove(self)

        
def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/chat", ChatWebSocket),
        (r"/old", PreviousMessagesHandler),
        (r"/js/(.*)", tornado.web.StaticFileHandler, {'path': js_folder}),
        (r"/css/(.*)", tornado.web.StaticFileHandler, {'path': css_folder}),
    ])


def main():
    app = make_app()
    app.listen(int(options.port))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()

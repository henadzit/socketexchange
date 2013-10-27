import collections

from flask import Flask, request, render_template, Response
from gevent import monkey
from socketio import socketio_manage
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer

app = Flask(__name__)
app.debug = True

monkey.patch_all()


_data = collections.defaultdict(list)


class SessionNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    class IncorrectSession(Exception):
        pass

    def initialize(self):
        self.session['slug'] = self.request['slug']

    def on_get(self):
        history = _data[self.slug]
        if history:
            pkt = self.__build_change_packet(history[-1])
            self.socket.send_packet(pkt)

        return True

    def on_change(self, content):
        print _data
        _data[self.slug].append(content)
        pkt = self.__build_change_packet(content)

        for sid, socket in self.socket.server.sockets.iteritems():
            if 'slug' not in socket.session:
                continue

            if self.socket != socket and self.slug == socket.session['slug']:
                socket.send_packet(pkt)

        return True

    @property
    def slug(self):
        return self.session['slug']

    def __build_change_packet(self, content):
        return dict(type='event', name='change',
                    args=dict(content=content))

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    try:
        socketio_manage(request.environ, {'': SessionNamespace}, dict(slug=request.args.get('slug')))
    except:
        app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()


@app.route('/<path:slug>')
def session(slug):
    return render_template('session.html', slug=slug)



if __name__ == '__main__':
    # app.run()
    SocketIOServer(('', 5000), app, resource="socket.io").serve_forever()
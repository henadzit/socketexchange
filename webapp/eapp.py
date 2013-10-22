from datetime import datetime
from flask import Flask, request, render_template, Response
from gevent import monkey
from socketio import socketio_manage
from socketio.mixins import RoomsMixin, BroadcastMixin
from socketio.namespace import BaseNamespace
from socketio.server import SocketIOServer

app = Flask(__name__)
app.debug = True

monkey.patch_all()


class SessionNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    """TODO: specify packet formats
    """
    def __init__(self, *args, **kwargs):
        super(SessionNamespace, self).__init__(*args, **kwargs)
        self.session['data'] = (datetime.min, None)
        self.session['slug'] = ''

    def on_init(self, msg):
        # slug = msg['slug']
        slug = ''
        last_data = self.session['data']

        for session in self.__sessions(slug):
            if session['data'][0] > last_data[0]:
                last_data = session['data']

        if last_data != self.session['data']:
            pkt = dict(type="event")
            self.socket.send_packet(pkt)

        return True

    def on_change(self, msg):
        pkt = dict(type="event",
                   name='change',
                   args=msg)

        for sid, socket in self.socket.server.sockets.iteritems():
            if self.socket != socket:
                socket.send_packet(pkt)

        return True

    def __sessions(self, slug):
        return (socket.session for sid, socket in self.socket.server.sockets.iteritems()
                if self.socket != socket and socket.session['slug'] == slug)


@app.route('/socket.io/<path:slug>')
def socketio(slug):
    try:
        socketio_manage(request.environ, {'': SessionNamespace}, request)
    except:
        app.logger.error("Exception while handling socketio connection", exc_info=True)

    return Response()


@app.route('/<path:slug>')
def session(slug):
    return render_template('session.html')

if __name__ == '__main__':
    # app.run()
    SocketIOServer(('', 5000), app, resource="socket.io").serve_forever()
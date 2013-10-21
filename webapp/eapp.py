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
    def __init__(self, *args, **kwargs):
        super(SessionNamespace, self).__init__(*args, **kwargs)
        # self.session['slug'] =

    def on_init(self, msg):
        pkt = dict(type="event",
                   name='change',
                   args=msg)
        print dir(request)


    def on_change(self, msg):
        pkt = dict(type="event",
                   name='change',
                   args=msg)

        for sid, socket in self.socket.server.sockets.iteritems():
            if self.socket != socket:
                socket.send_packet(pkt)

        return True


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
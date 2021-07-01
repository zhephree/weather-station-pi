from aiohttp import web
import socketio

sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

async def index(request):
    """Serve the client-side application."""
    return web.Response(text='OK', content_type='text/html')

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    print("message ", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

# app.router.add_static('/static', 'static')
app.router.add_get('/', index)

def listen(port):
    web.run_app(app, port=port)


# @sio.event
# def connect(sid, environ):
#     print('connect ', sid)

# @sio.event
# def my_message(sid, data):
#     print('message ', data)

# @sio.event
# def disconnect(sid):
#     print('disconnect ', sid)

# if __name__ == '__main__':
#     eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
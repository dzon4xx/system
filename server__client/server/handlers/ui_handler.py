import tornado.web
from server_client.server.models.room import Room

rooms = Room.items
paths = (r'/ui/ui.html', r'/ui/sidebar_left.html', r'/ui/sidebar_right.html', r'/ui/system?')
data = {r'/ui/ui.html' :  (r'/ui/sidebar_left.html', r'/ui/sidebar_right.html', rooms),
             r'/ui/sidebar_left.html': (rooms,)}

class UiHandler(tornado.web.RequestHandler):
    def get(self):
        
        if self.request.path == '/ui/system':
            for room in rooms.values():
                self.write(room.get_html())
        else:       
            self.render(self.request.path.strip('/'), rooms=rooms)





      
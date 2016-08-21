import tornado.web
from server_client.server.models.room import Room


class UiHandler(tornado.web.RequestHandler):
    def get(self):
        if self.request.path == '/ui/navigation_bar':
            self.render('navigation_bar.html', rooms=Room.items.values())
                    
        elif self.request.path == '/ui/system':
            for room in Room.items.values():
                self.write(room.get_html())






      
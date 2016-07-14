class a():
    def __init__(self, *args):
        self.b, self.c = args

d = a(*(1,2))
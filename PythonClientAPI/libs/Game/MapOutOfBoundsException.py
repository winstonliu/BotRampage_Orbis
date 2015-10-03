class MapOutOfBoundsException(Exception):
    def __init__(self, arg):
        self.msg = arg

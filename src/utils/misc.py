class QuitGameException(Exception):
    pass

class ScreenWrapper:
    def __init__(self, screen):
        self.screen = screen

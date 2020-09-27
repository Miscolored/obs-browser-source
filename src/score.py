import json

class Score():
    """
    Holds the wins and losses
    """
    
    def __init__(self, name = "noname"):
        # order of object variables matters because we render json with vars()
        self.name = name
        self.win = 0
        self.loss = 0
        self.id = id(self)

    def emit(self):
        return {
            'name': self.name,
            'win': self.win,
            'loss': self.loss
        }

    def increment_win(self):
        self.win += 1

    def decrement_win(self):
        self.win -= 1

    def increment_loss(self):
        self.loss += 1

    def decrement_loss(self):
        self.loss -= 1

    def reset(self):
        self.win, self.loss = 0, 0

    def get_name(self):
        return self.name

    def get_win(self):
        return self.win

    def get_loss(self):
        return self. loss

    def get_id(self):
        return self.id

class Config:
    def __init__(self):
        # Game Constraints
        self.board_size_x = 1500
        self.board_size_y = 400
        self.heading = 30
        self.unit_size = 10

        # unit types
        self.friendly = 0
        self.enemy = 1

        # unit states
        self.move = 0
        self.attack = 1
        self.disperse = 2

        # emission types
        self.spectrum = 0
        self.thermal = 1
        self.visual = 2
        self.direct_fire = 3
        self.lifespan = 50

        # Colors
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.blue = (0, 191, 255)
        self.white = (255, 255, 255)
        self.green = (0, 255, 0)
        self.orange = (254, 216, 177)

        # directions
        self.NW = (-1, -1)
        self.N = (0, -1)
        self.NE = (1, -1)
        self.E = (1, 0)
        self.SE = (1, 1)
        self.S = (0, 1)
        self.SW = (-1, 1)
        self.W = (-1, 0)
        self.none = (0, 0)

        self.dir_list = [self.none, self.NW, self.N, self.NE, self.E, self.SE, self.S, self.SW, self.W]
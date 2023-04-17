from gamegrid import *

class Fisch(Actor):
    def act(self):
        self.move()

makeGameGrid(10,10,48,Color.gray)
nemo = Fisch('/home/kreuterkeule/Documents/python/game/textures/textures/Stone.png')
addActor(nemo, Location(0,0))
show()
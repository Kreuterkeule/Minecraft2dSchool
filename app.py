# Openworld Game in 2d von Moritz Siefke orientiert an Minecraft von Mojang
#
# Geschrieben in Jython
#
# Zum spielen die Geschwindigkeit der Gameticks auf Max stellen
#
# Dank geht an Dman49 fuer ein Teil der Texturen.
#
# Verwendet wurde das Minecraft 2d Texturepack von Dman49 zu finden unter https://www.moddb.com/groups/minecraft-community/addons/original-minecraft-2d-psp-texture-pack

from gamegrid import *
from random import randint
from java.awt import Point
import time

# change this to the location, where your textures are stored, textures should be 48x48 png pictures and named as used in Programm. For easy use use the Texturepack from Dman49. Kee[ in mind, that the texturepack i use is a heavily modified version of Dman49s.

absPath = '/home/kreuterkeule/Documents/python/game/textures/textures/'

# Group of blocks available to choose random for building the ground

ground = []

# set rareness

rarenesses = {
'Amazonite.png': 1,
'Sapphire.png': 1,
'Diamond.png': 1,
'Gold.png': 1,
'Iron.png': 4,
'Coal.png': 14,
'Aluminium.png': 3,
'Stone.png': 120,
'Gravel.png': 10,
'Ruby.png': 2,
}

# Add Blocks to Ground depending on their Rareness

for block in rarenesses:
    for i in range(rarenesses[block]):
        ground.append(block)

# setting up Global Mouse actions

# right click on actor

def mouseDownOnActor(actor, mouse, spot):
    playerNextToActor = False
    for addX in [-1,0,1]:
        for addY in [-1,0,1]:
            actors = getActorsAt(Location(actor.getX() + addX, actor.getY() + addY))
            if len(actors) > 0:
                for el in actors:
                    if el.actType == 'player':
                        playerNextToActor = True
    if actor.actType != 'player' and actor.actType != 'app:BedRock' and playerNextToActor: # don't remove irremovable blocks and players
        actor.removeSelf()

def countJump(actor):
    if actor.jumpCounter <= 450: # <- set jump duration in gameTicks
        actor.jumpCounter += 1
    else:
        actor.jumpActive = not actor.jumpActive
        actor.jumpCounter = 0
        actor.setDirection(90)
        actor.move()

def countJumpCooldown(actor):
    if actor.jumpCooldownCounter <= 600: # <- set jump duration in gameTicks
        actor.jumpCooldownCounter += 1
    else:
        actor.jumpCooldownActive = not actor.jumpCooldownActive
        actor.jumpCooldownCounter = 0

# hotbar loader

def loadHotBar(player):
    for i in range(10):
        x = 0
        if i != 0 or i != 1: # warum auch immer die != 1 notwedig ist es funktionier <!-- never change a running system -->
            x = i + 5
        elif i == 0:
            x = 14
        else:
            x = 5
        if i != 9:
            f = i+1
        else:
            f = 0
        getOneActorAt(Location(x, 19)).removeSelf()
        slotItems = player.items
        item = ItemPlaceholder(str(absPath)+str(slotItems[f]))
        addActor(item, Location(x, 19))
        player.addCollisionActor(item)
        slot = HotbarSlot()
        addActor(slot, Location(x, 19))
        player.addCollisionActor(item)



# generators to generate the Terrain

def generateBedRock(player):
    for x in range(20):
        actors = getActorsAt(Location(x, 19))
        for actor in actors:
            actor.removeSelf()
        block = BedRock(str(str(absPath))+'Bedrock.png')
        addActor(block, Location(x, 19))
        player.addCollisionActor(block)

def generateGrass(player, heights): # generate Grass and Sand at Top layer
    for x in range(20):
        y = 19 - heights[x]
        if y < 9:
            block = Grass(str(str(absPath))+'Grass.png')
            addActor(block, Location(x, y))
            block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
            player.addCollisionActor(block)
        else:
            block = GravityBlock(str(str(absPath))+'Sand.png')
            addActor(block, Location(x, y))
            block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
            player.addCollisionActor(block)

def generateGround(player): # Generate basic terrain
    print(' Generate World')
    heights = []
    for i in range(20):
        if i == 0:
            heights.append(randint(7,13))
        else:
            availHeights = []
            for j in [-1,0,1]: # these are all "jumpable" heights
                heightBefore = heights[i-1]
                if heightBefore+j <= 13 and heightBefore+j >= 7:
                    availHeights.append(heightBefore+j)
            heights.append(availHeights[randint(0,len(availHeights)-1)])
    for x, height in enumerate(heights):
        for i in range(height):
            y = 19 - i
            Type = str(ground[randint(0,len(ground)-1)])
            if Type != 'Gravel.png':
                block = Block(str(absPath)+Type)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, Location(x, y))
                player.addCollisionActor(block)
            elif Type == 'Gravel.png':
                block = GravityBlock(str(absPath)+Type)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, Location(x, y))
                player.addCollisionActor(block)
    generateGrass(player, heights)
    generateTrees(player, heights)
    generateWater()
    print(' World generated successfull')

def generateWater(): # fill world with water
    print('> flooding World with water')
    counter = 0
    for x in range(20):
        for i in range(11):
            y = 19 - i
            actor = getOneActorAt(Location(x,y))
            if actor == None:
                fluid = Fluid(str(str(absPath))+'Water.png')
                fluid.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(fluid, Location(x,y))
                counter += 1
    print('> World flooded, it took ' + str(counter) + ' blocks of water')

def growTree(tree, heights, section, player): # generate single Tree
    print('>>> growing Tree ' + str(section + 1) + ' of 3')
    print('>>> gowing ' + tree['size'] + ' tree')
    x = tree['pos'] + (section * 7)
    if x < 20:
        y = 19 - (heights[x] + 1)
        if (19 - heights[x]) < (19 - 9) and getOneActorAt(Location(x, y + 1)).actType == 'app:grass_block': # trees can only grow on grass blocks
            size = 0
            if tree['size'] == 'normal':
                size = 2
            elif tree['size'] == 'large':
                size = 3
            elif tree['size'] == 'larger':
                size = 4
            print('>>>> growing Stem')
            for addToY in range(size):
                block = Block(str(str(absPath)+'Log_1.png'))
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, Location(x, y - addToY))
                player.addCollisionActor(block)
                print('>>>>> stem block ' + str(addToY + 1) + ' of ' + str(size) + ' Done.')
            print('>>>> Stem... Done.')
            for i in range(2):
                for addToX in [-2,-1,0,1,2]:
                    block = Block(str(str(absPath)+'Leaf_2.png'))
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    addActor(block, Location(x + addToX, y - size - i))
                    player.addCollisionActor(block)
            for addToX in [-1,0,1]:
                block = Block(str(str(absPath)+'Leaf_2.png'))
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, Location(x + addToX, y - size - 2))
                player.addCollisionActor(block)
            print('>>> Tree... Done.')
        else:
            print('>>> Tree position under water... continue.')
    else:
        print('>>> Tree position out of range... continue.') # tree generated out of the world

def growTrees(player, trees, heights): # call grow tree function for each tree
    print('>> growingTrees')
    for index, tree in enumerate(trees):
        growTree(tree, heights, index, player)
    print('>> growing Trees... Done.')

def generateTrees(player, heights):
    print('> Generating Trees')
    trees = ['normal','large', 'larger']
    treesToGrow = []
    for i in range(3):
        treesToGrow.append({'size': trees[randint(0,2)], 'pos': randint(0,6)})
    growTrees(player, treesToGrow, heights)

# class Player
#
# attributes:
#
# hotbaritems
# jump status
# act function obviously
# collision function to move back to position before collision
# mouse event manager for placing blocks

class Player(Actor, GGMouseListener):
    actType = 'player'
    jumpCounter = 0
    jumpCooldownCounter = 0
    jumpActive = False
    jumpCooldownActive = False
    selectedSlot = 1
    items = {
        0: 'Stone.png',
        1: 'Log_1.png',
        2: 'Glass.png',
        3: 'Brick.png',
        4: 'Water.png',
        5: 'TNT_0.png',
        6: 'Trapdoor_1.png',
        7: 'Ladder.png',
        8: 'Gravel.png',
        9: 'Cobblestone.png',
    }
    def __init__(self):
        Actor.__init__(self, '/home/kreuterkeule/Documents/python/game/textures/textures/Head.png')
    def act(self):
        if self.nbCycles % 300 == 0 and not self.jumpActive:
            self.setDirection(90)
            self.move()
        if self.jumpActive:
            countJump(self)
        if self.jumpCooldownActive:
            countJumpCooldown(self)
    def collide(self, actor1, actor2):
        if actor2.actType != 'app:trapdoor':
            self.setDirection(self.getDirection() + 180)
            self.move()
            self.setDirection(self.getDirection() - 180)
            return 10
        else:
            if actor2.actType == 'app:trapdoor':
                if actor2.opened:
                    return 10
                else:
                    self.setDirection(self.getDirection() + 180)
                    self.move()
                    self.setDirection(self.getDirection() - 180)
                    return 10
    def mouseEvent(self, mouse):
        mouseLocation = toLocationInGrid(mouse.getX(), mouse.getY())
        actor = getOneActorAt(mouseLocation)
        blockToPlaceOnIsPresent = False
        isPlayerPresent = False
        for addX in [-1,0,1]:
            for addY in [-1,0,1]:
                actors = getActorsAt(Location(mouseLocation.getX() + addX,mouseLocation.getY() + addY))
                for el in actors:
                    if el.actType == 'player':
                        isPlayerPresent = True
        for addX in [-1,1]:
            blockToPlaceOn = getOneActorAt(Location(mouseLocation.getX() + addX,mouseLocation.getY()))
            if blockToPlaceOn != None:
                if blockToPlaceOn.actType != 'player' and blockToPlaceOn.actType != 'fluid':
                    blockToPlaceOnIsPresent = True
        for addY in [-1,1]:
            blockToPlaceOn = getOneActorAt(Location(mouseLocation.getX(),mouseLocation.getY() + addY))
            if blockToPlaceOn != None:
                if blockToPlaceOn.actType != 'player' and blockToPlaceOn.actType != 'fluid':
                    blockToPlaceOnIsPresent = True
        if actor == None:
            if blockToPlaceOnIsPresent and isPlayerPresent:
                if self.items[self.selectedSlot] != 'Water.png' and self.items[self.selectedSlot] != 'TNT_0.png' and self.items[self.selectedSlot] != 'Trapdoor_1.png' and self.items[self.selectedSlot] != 'Ladder.png' and self.items[self.selectedSlot] != 'Gravel.png':
                    block = Block(str(str(absPath)+str(self.items[self.selectedSlot])))
                    addActor(block, mouseLocation)
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    self.addCollisionActor(block)
                if self.items[self.selectedSlot] == 'Trapdoor_1.png':
                    block = Trapdoor()
                    addActor(block, mouseLocation)
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    self.addCollisionActor(block)
                if self.items[self.selectedSlot] == 'TNT_0.png':
                    block = TNTBlock()
                    addActor(block, mouseLocation)
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    self.addCollisionActor(block)
                if self.items[self.selectedSlot] == 'Ladder.png':
                    block = Ladder()
                    addActor(block, mouseLocation)
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                if self.items[self.selectedSlot] == 'Gravel.png':
                    block = GravityBlock(str(absPath)+str(self.items[self.selectedSlot]))
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    addActor(block, mouseLocation)
                    block.setDirection(270)
                    block.move()
                    self.addCollisionActor(block)
                if self.items[self.selectedSlot] == 'Water.png':
                    block = FluidHandPlaced(str(absPath)+self.items[self.selectedSlot])
                    block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                    addActor(block, mouseLocation)
        elif actor.actType == 'fluid':
            if self.items[self.selectedSlot] != 'Water.png' and self.items[self.selectedSlot] != 'TNT_0.png' and self.items[self.selectedSlot] != 'Trapdoor_1.png' and self.items[self.selectedSlot] != 'Ladder.png' and self.items[self.selectedSlot] != 'Gravel.png':
                actor.removeSelf()
                block = Block(str(str(absPath)+str(self.items[self.selectedSlot])))
                addActor(block, mouseLocation)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                self.addCollisionActor(block)
            if self.items[self.selectedSlot] == 'Trapdoor_1.png':
                actor.removeSelf()
                block = Trapdoor()
                addActor(block, mouseLocation)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                self.addCollisionActor(block)
            if self.items[self.selectedSlot] == 'TNT_0.png':
                actor.removeSelf()
                block = TNTBlock()
                addActor(block, mouseLocation)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                self.addCollisionActor(block)
            if self.items[self.selectedSlot] == 'Ladder.png':
                actor.removeSelf()
                block = Ladder()
                addActor(block, mouseLocation)
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
            if self.items[self.selectedSlot] == 'Gravel.png':
                actor.removeSelf()
                block = GravityBlock(str(absPath)+self.items[self.selectedSlot])
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, mouseLocation)
                block.setDirection(270)
                block.move()
                self.addCollisionActor(block)
            if self.items[self.selectedSlot] == 'Water.png':
                actor.removeSelf()
                block = FluidHandPlaced(str(absPath)+self.items[self.selectedSlot])
                block.addMouseTouchListener(mouseDownOnActor, GGMouse.lPress)
                addActor(block, mouseLocation)
        else:
            if actor.actType == 'app:trapdoor':
                actor.opened = not actor.opened
                actor.showNextSprite()
            if actor.actType == 'app:TNT':
                actor.explode()

# hotbar classes

class ItemPlaceholder(Actor):
    actType = 'app:BedRock'

class HotbarSlot(Actor):
    actType = 'HotbarSlot'
    def __init__(self):
        Actor.__init__(self, str(absPath) + 'Inv.png', 2)

# function for act of fluid

def floodWater(self,addX,addY,handPlaced):
    used = False
    actors = getActorsAt(Location(self.getX() + addX, self.getY() + addY))
    for el in actors:
        if el != None:
            if  el.actType != 'player':
                used = True
    if not used:
        if ((self.getY() + addY) >= 9 or handPlaced) and (self.getY() + addY) <= 19 and (self.getX() + addX) <= 19 and (self.getX() + addX) >= 0:
            if handPlaced:
                fluid = FluidHandPlaced(str(str(absPath)+'Water.png'))
                addActor(fluid, Location(self.getX() + addX, self.getY() + addY))
                fluid.addMouseTouchListener(mouseDownOnActor, GGMouse.lClick)
            else:
                fluid = Fluid(str(str(absPath)+'Water.png'))
                addActor(fluid, Location(self.getX() + addX, self.getY() + addY))
                fluid.addMouseTouchListener(mouseDownOnActor, GGMouse.lClick)

# block and fluid Classes to identify the diffrence and add fluid spreading

class Trapdoor(Actor):
    actType = 'app:trapdoor'
    opened = False
    def __init__(self):
        Actor.__init__(self, str(absPath) + 'Trapdoor.png', 2)

class Ladder(Actor):
    actType = 'app:ladder'
    def __init__(self):
        Actor.__init__(self, str(absPath) + 'Ladder.png')

class Block(Actor):
    actType = 'block'
    #def __init__(self):
        #steve.addCollisionListener(self) waehre toll wenn das gehen wuerde geht aber nicht anscheinend gibt einen error bei einem addActor(Block('some/path') es seien 2 anstatt 1 parameter in der __init__ function gegeben.

class TNTBlock(Actor):
    actType = 'app:TNT'
    egnited = False
    def __init__(self):
        Actor.__init__(self, str(absPath) + 'TNT.png', 2)
    def explode(self):
        self.egnited = True
        for i in range(6):
            self.showNextSprite()
            delay(500)
        for addX in [-1, 0, 1]:
            for addY in [-1, 0 ,1]:
                actors = getActorsAt(Location(self.getX() + addX, self.getY() + addY))
                for actor in actors:
                    if actor.actType != 'player' and actor.actType != 'app:TNT' and actor.actType != 'app:BedRock' and actor.actType != 'HotbarSlot':
                        actor.removeSelf()
                    if actor.actType == 'app:TNT':
                        if actor.egnited:
                            actor.removeSelf()
                        else:
                            actor.explode()
        for addX in [-2,2]:
            for addY in [2,1,0,-1,-2]:
                actors = getActorsAt(Location(self.getX() + addX, self.getY() + addY))
                for actor in actors:
                    if actor.actType != 'player' and actor.actType != 'app:TNT' and actor.actType != 'app:BedRock' and actor.actType != 'HotbarSlot' and randint(0,1) == 1:
                        actor.removeSelf()
                    if actor.actType == 'app:TNT':
                        if actor.egnited:
                            actor.removeSelf()
                        else:
                            actor.explode()
        for addY in [-2,2]:
            for addX in [2,1,0,-1,-2]:
                actors = getActorsAt(Location(self.getX() + addX, self.getY() + addY))
                for actor in actors:
                    if actor.actType != 'player' and actor.actType != 'app:TNT' and actor.actType != 'app:BedRock' and actor.actType != 'HotbarSlot'  and randint(0,1) == 1:
                        actor.removeSelf()
                    if actor.actType == 'app:TNT':
                        if actor.egnited:
                            actor.removeSelf()
                        else:
                            actor.explode()

# classes for blocks

# irremovable block called Bedrock

class BedRock(Actor):
    actType = 'app:BedRock'

# grass block class, needed for tree generation

class Grass(Actor):
    actType = 'app:grass_block'

# Gravity block is a block, whitch falls down.

class GravityBlock(Actor):
    actType = 'app:gravity_block'
    def act(self):
        if self.nbCycles % 300 == 0:
            actorBelow = getOneActorAt(Location(self.getX(), self.getY() + 1))
            if actorBelow == None:
                self.setDirection(90)
                self.move()
            elif actorBelow.actType == 'fluid':
                actorBelow.removeSelf()
                self.setDirection(90)
                self.move()

# fluid is a type, which spreads and from which no player has contact

class FluidHandPlaced(Actor):
    actType = 'fluid'
    def act(self):
        if self.nbCycles % 300 == 0:
            for addX in [-1,0,1]:
                floodWater(self, addX, 0,True)
            for addY in [0,1]:
                floodWater(self, 0, addY,True)

class Fluid(Actor):
    actType = 'fluid'
    def act(self):
        if self.nbCycles % 300 == 0:
            for addX in [-1,0,1]:
                floodWater(self, addX, 0,False)
            for addY in [0,1]:
                floodWater(self, 0, addY,False)


# Player Control with arrow-keys

def keyCallback(e):
    key = e.getKeyCode()
    if (key == 65 or key == 37) and steve.getX() > 0: #left
        steve.setDirection(180)
    elif (key == 40 or key == 83):
        steve.setDirection(90)
        steve.move()
    elif (key == 32 or key == 87 or key == 38) and getOneActorAt(Location(steve.getX(),steve.getY()+1)) != None: #up if not already up
        steve.setDirection(270)
        steve.jumpActive = True; # disables gravity and the ability to jump again for a certain time, due to activation on jumpCounter in the actor itself
        steve.jumpCooldownActive = True;
    elif (key == 68 or key == 39) and steve.getX() < 19: #right
        steve.setDirection(0)
    elif key == 48: #0
        steve.selectedSlot = 0
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(14, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 49: #1
        steve.selectedSlot = 1
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(5, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 50: #2
        steve.selectedSlot = 2
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(6, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 51: #3
        steve.selectedSlot = 3
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(7, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 52: #4
        steve.selectedSlot = 4
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(8, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 53: #5
        steve.selectedSlot = 5
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(9, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 54: #6
        steve.selectedSlot = 6
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(10, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 55: #7
        steve.selectedSlot = 7
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(11, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 56: #8
        steve.selectedSlot = 8
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(12, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    elif key == 57: #9
        steve.selectedSlot = 9
        for i in range(10):
            actors = getActorsAt(Location(5+i, 19))
            for actor in actors:
                if actor.actType == 'HotbarSlot':
                    actor.show(0)
        actors = getActorsAt(Location(13, 19))
        for actor in actors:
            if actor.actType == 'HotbarSlot':
                actor.show(1)
    else:
        return
    steve.move()


# main

makeGameGrid(20, 20, 48, None, '/home/kreuterkeule/Documents/python/game/textures/textures/background.jpeg', keyPressed = keyCallback)
setSimulationPeriod(4)
steve = Player()
addActor(steve, Location(0,0))
generateGround(steve)
generateBedRock(steve)
loadHotBar(steve)
ranX = randint(0,19) # get a random x coordinate to place the Player "Steve"
calculatedY = 19 # set calculated Y to lowest Point in Grid
while(True):
    actor = getOneActorAt(Location(ranX,calculatedY))
    if(actor != None):
        calculatedY -= 1
    else:
        break
steve.setLocation(Location(ranX, calculatedY))
addMouseListener(steve, GGMouse.rClick)
addMouseListener(steve, GGMouse.rDClick)
show()
doRun()

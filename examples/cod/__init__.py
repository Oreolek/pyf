# cod.py
'''Python source. Used to define the actual game logic.'''
from pyf import items, game

class Game(game.Game):
	'''First we subclass the Game object to create our own game.'''
	script = open('cod.script.xml')
	'''Script is defined as a file-like object.'''
	
	def ending(self, output):
		'''Called after game.end() is called.'''
		if Bar.inst.counter > 1:
			'''Output object is used for writing all responses for the player.'''
			output.write("*** You have lost ***")
		else:
			output.write("*** You have won ***")
			
game = Game()

class Player(items.Actor):
	pass
class Foyer(items.Room):
	pass
class Cloakroom(items.Room):
	pass
	
class Bar(items.Room):
	def init(self):
		self.counter = 0
		self.addEventListener(self.EVT_OWNED_ITEM_HANDLE, (self, barItemHandled))
		'''EVT_OWNED_ITEM_HANDLE is fired before the player tries to handle
		items in a container, this time a room.'''

def barItemHandled(self, event):
	'''The user can't interact with objects in the dark room, but we still need to
	show an alternative message and add to our counter.'''
	
	if not self.Dark.lit:
		self.counter += 1
		if self.counter > 1:
			event.output.write("It's best not to mess around in the dark!")
		else:
			event.output.write("In the dark? You could easily disturb something.")
	
class Hook(items.Item):
	def handle(self, sentence, output):
		if sentence == 'hang cloak on *self':
			Cloak.inst.move(self)
			'''Cloak.inst = cloak instance'''
			output.write("You finish hanging your cloak on the hook.")
		
class Message(items.Item):
	def handle(self, sentence, output):
		if sentence == 'read *self' or sentence == 'examine *self':
			output.write('The message, neatly marked in the sawdust, reads...', False)
			self.game.end(output)
			'''End the game.'''
			
def cloakMoved(self, event):
	'''This event handler is called to check if the cloak can be moved and return
	a response if not.'''
	if event.destination not in (Player, Hook, Cloakroom):
		if event.output:
			event.output.write("This isn't the best place to leave a smart cloak lying around.")

class Cloak(items.Item):
	def init(self):
		'''Listen to move events.'''
		self.addEventListener(self.EVT_MOVED, (self, cloakMoved))

'''Create the game world based on our script.'''
game.initFromScript(locals())

'''Set Player object as the actor.'''
game.setActor(Player.inst)

if __name__ == '__main__':
	'''Finally we need an interface so that you can actually play the game. '''
	import pyf.interface
	pyf.interface.runGame(game)
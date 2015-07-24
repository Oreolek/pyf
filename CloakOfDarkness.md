# Cloak of Darkness #

Cloak of Darkness is an interactive fiction by Roger Firth designed to demonstrate differences between IF authoring systems. You can check out its different implementations on [Firth's site](http://www.firthworks.com/roger/cloak/). For the PyF implementation, see below.

```
<?xml version="1.0" encoding="UTF-8" ?>
<!-- cod.script.xml -->
<!-- Script is used to define the actual form of the game world, how objects
are placed throughout it, and their text content. -->
<script xmlns:props="pyf.props">
	<!-- Import module pyf.props as an XML namespace. -->
	<game>
		<!-- game is our Game object instantiated in the source -->
		<attr>
			<!-- Tags inside <attr> are assigned to the object dict after 
			instantiation. That means after our script is read game.name is 
			"Cloak of Darkness" and game.author is "Roger Firth" and so on. -->
			<name>Cloak of Darkness</name>
			<author>Roger Firth</author>
			<version>1.0</version>
			<description>Hurrying through the rainswept November night, you're glad to 
				see the bright lights of the Opera House. It's surprising that there 
				aren't more people about but, hey, what do you expect in a 
				cheap demo game...?</description>
				
		</attr>
	</game>
	
	<Foyer name="Foyer of the Opera House">
		<!-- Foyer is a class defined in the source - here we instantiate it with the name
		"Foyer of the Opera House". -->
		
		<exits>
			<west><Cloakroom /></west>
			<south><Bar /></south>
			<!-- Cloakroom and Bar are classes defined in the source. -->
			<north>You've only just arrived, and besides, the weather 
			outside seems to be getting worse.</north>
		</exits>

		<!-- ldesc is automatically turned into the item's long description. -->
		<ldesc>You are standing in a spacious hall, splendidly decorated in red 
		and gold, with glittering chandeliers overhead. The entrance from 
		the street is to the north, and there are doorways south and west.</ldesc>
		
		<Player>
			<!-- Player class defined in the source. Any class node that's contained in
			another class node is automatically moved to the containing object. So after
			this is read, Player is moved to its starting place in Foyer. -->
			
			<ldesc>As handsome as ever.</ldesc>
			
			<Cloak name="cloak" adjective="handsome, velvet, dark, black, velvet, satin">
				<ldesc>A handsome cloak, of velvet trimmed with satin, and slightly 
				spattered with raindrops. Its blackness is so deep that it almost 
				seems to suck light from the room.</ldesc>
				
				<!-- Mobile is a property class residing in pyf.props. Here the property
				is instantiated and moved to the cloak object. This allows the player
				to move the cloak, take and drop it. -->
				<props:Mobile />
				
				<!-- Wearable defines object as something you can wear. -->
				<props:Wearable>
					<!-- Values are by default evaluated as strings. Specifying type as
					"bool" here allows the XML parser to evaluate the value as 
					bool(True). Here we're saying that the cloak is worn by default. -->
					<attr>
						<worn type="bool">True</worn>
					</attr>
				</props:Wearable>
				
				<props:LightSource>
					<attr>
						<inverse type="bool">True</inverse>
					</attr>
					<!-- Taking the cloak into a room will make it dark, 
					instead of lit. -->
				</props:LightSource>
			</Cloak>
		</Player>

	</Foyer>
	
	<Cloakroom name="Cloakroom">
		
		<ldesc>The walls of this small room were clearly once lined with hooks, 
		though now only one remains. The exit is a door to the east.</ldesc>
		
		<exits>
			<east><Foyer /></east>
		</exits>
		<props:Room/>
		<!-- Automatically lists undescribed things in the room. We add it here since
		it's possible to drop the cloak on the floor. -->
		
		<Hook name="hook, peg" adjective="brass, small">
			<ldesc>It's just a small brass hook.</ldesc>
			
			<!-- Allow putting things on the hook. -->
			<props:Surface />
		</Hook>
		
	</Cloakroom>
	
	<Bar name="Foyer bar">
		<exits>
			<north><Foyer /></north>
		</exits>

		<ldesc>The bar, much rougher than you'd have guessed after the opulence of the 
		foyer to the north, is completely empty. There seems to be some sort of message 
		scrawled in the sawdust on the floor.</ldesc>
		
		<props:Dark>
			<!-- The room is lit by default, taking the cloak into the room 
			makes it dark. -->
			<attr>
				<light type="bool">True</light>
			</attr>
		</props:Dark>
		
		<Message name="message, sawdust"/>
	</Bar>
</script>
```

```
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
```
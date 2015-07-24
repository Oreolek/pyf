# Work in progress #

This article is work in progress. For an example of a working game, check [Cloak of Darkness in PyF](CloakOfDarkness.md).

# Introduction #

This tutorial goes through the process of creating a basic game in PyF. It expects you to know the basics of object-oriented programming in Python; if you're still learning, I warmly recommend  [A Byte of Python](http://www.swaroopch.com/notes/Python_en:Table_of_Contents) by Swaroop C H. You can read it online for free at his site.

A typical PyF game is split into 2 files, your Python source and an external script. Most of the time you'll be working on the script as it contains the most important part of your game: the actual text. The Python file is there just to set up the game and add any functionality that's not included in the default library.

# The Script #

Let's take a look at a basic script file:
```
<Game>
	<Room name="Furnace room, room"
		ldesc="You're stuck in a tiny furnace room. Right now the heat is 
			unbearable and it seems to be only rising.">

		<Player name="yourself" />

		<Furnace name="furnace, boiler" />
	</Room>
</Game>
```
If you've ever seen HTML code this should look familiar. You open tags with `<something>` and close them with `</something>`. Anything contained within these tags is their content. In PyF this works somewhat analogously to the real world; here we have a room with the player and a furnace inside it.

# The Source #

Before we can run this game, we need to write some Python code to load the script and define the classes we use in the script.
```
from pyf import items, game, interface, props

class Game(game.Game):
	pass

class Room(items.Room):
	pass
	
class Player(items.Actor):
	pass
	
class Furnace(items.Item):
	pass
	
game = game.createFromScript(open('script.xml'), locals())
game.actor = Player.inst
interface.runGame(game)
```
`Game`, `Room`, `Player` and `Furnace` in the script file refer to these classes. What the script does is instantiate these classes and move them to their owner. In the case of `Room` it also adds a description to the object. If we want to add descriptions to the other objects, we'll simply add `ldesc="..."` to them:
```
...
	<Player name="yourself"
		ldesc="If you want to find out more about yourself, maybe you should 
			head out to the real world."
	/>

	<Furnace name="furnace, boiler"
		ldesc="The furnace seems to be malfunctioning somehow; it shouldn't be this hot."
	/>
...
```
If you save the script as `script.xml` you can now run the game.

# Interacting With the World #
Right now our game isn't very exciting. There's only one room and you can't actually interact with the objects in it. Let's give our player something to work with.
```
<Game xmlns:props="pyf.props">
	...
		<Player name="yourself"
			ldesc="If you want to find out more about yourself, maybe you should 
				head out to the real world.">
				
			<Screwdriver name="screwdriver" adjective="small, metallic"
				ldesc="It's a small metallic screwdriver.">
				<props:Mobile />
			</Screwdriver>
		</Player>
	...
</Game>
```
The first thing we need to do is import a Python module to use in our script. You can do this by adding an XML namespace to the `Game` tag. Here we import `pyf.props` from the PyF default library - it includes many properties that are typical in IF games. You can think of properties as building blocks of an object: they define a particular aspect of how an object works, and by stringing many of them together you can create objects that behave a lot like you would expect them to in the real world.

Here the player is carrying a screwdriver. Since the screwdriver is small enough to carry, it wouldn't make much sense if the player couldn't drop it: that's why we add the `props:Mobile` to the screwdriver. The prefix `props:` comes from the name of the module it resides in; if it were defined in our own source it would be simply `Mobile`. The property itself just allows the player to move the object like you could in the real world. It allows taking the object, dropping it, and pushing it around.

The screwdriver is a new object so let's change our source to reflect this.
```
class Screwdriver(items.Item):
	pass
```
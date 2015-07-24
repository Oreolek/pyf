PyF is a free, cross-platform Python library for writing interactive fiction. It aims to make writing interactive fiction easy and efficient without a need to learn a specialized language.

# What is... #

  * [Interactive fiction?](http://en.wikipedia.org/wiki/Interactive_fiction)
  * [Python?](http://en.wikipedia.org/wiki/Python_%28programming_language%29)

# What does PyF look like? #

Here's a simple hello world program in PyF:
```
from pyf import game, items, props, interface
class Game(game.Game):
	name = "Hello World!"
game = Game()

class Room(items.Room):
	name = "Field"
	props = props.Normal('You\'re lying on a vast field of flowers looking\
	up to the sky. The clouds seem to spell out the words "HELLO WORLD".')
game.addItem(Room())
	
class Player(items.Actor):
	owner = Room.inst
game.addItem(Player())

game.actor = Player.inst
interface.runGame(game)
```

This creates a game world, adding a single room with a description and the player object to it.

## Why choose PyF? ##
  * Because PyF allows separating the world model from the game logic, the game source code is easy to read.
  * PyF parser is very flexible. It can parse and match sentences of virtually endless complexity. Wildcard matches allow you to customize default responses very easily.
  * PyF is written in an interpreted language. That means that PyF is available on every platform that Python is ported to. So you can write a game and have it run on Windows, OS X and Linux without changing anything.
  * Unlike some other IF engines, PyF doesn't require you to learn a specialized language that you can only use to write IF.
  * In PyF you can easily handle any input not supported by the standard library. Adding new synonyms for your game is trivial.
  * PyF is designed to be completely modular. You can customize your game engine as much as you like, from changing the standard responses to completely rewriting the input handling process.

## How to get started? ##
  * [Download PyF](Download.md)
  * Read our [getting started guide](GettingStarted.md)
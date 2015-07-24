An XML-script is the standard way to define your world model in PyF. Its purpose is distinctly different from that of your Python source: to initiate the game, move things to their starting places and add text to them. Ideally everything that's visible to the player is defined in the script - this includes item descriptions, their starting places and their standard behaviour.

# Creating a script file #

```
<Game>
	<attr>
		<name>My Game</name>
		<author>My Name</author>
		<version>1.0</version>
		<description>This is shown before the game title.</description>
		<intro>This is shown after the game title and before the room description.</intro>
	</attr>
</Game>
```

As you can see, the XML file doesn't define a specific doctype for you to use. There aren't any hard restrictions on how you format your script, but there are some conventions and features you'll want to take advantage of. But first let's create a game from this script:

```
from pyf import game

class Game(game.Game):
	pass
	
game = game.createFromScript(open('script.xml'), {'Game': Game})
```

`game.createFromScript` is used to initiate your game according to a script. The first argument is a file like object containing your script. The second is a dict you want to use to map your classes. In this example we're just mapping `<Game>` to the class `Game` in our Python source; when the XML parser encounters the tag, it'll create an instance of the class and return it.

Tags in `<attr>` are assigned to the `Game` instance after instantiation - basically
```
<attr><author>John Doe</author></attr>
```
is the same as writing:
```
game.author = "John Doe"
```
By default the value of such assignment is a string. If you want to assign another type of value you can add the `type` attribute.
```
<age type="int">5</age>
<child type="bool">True</age>
```
This is done through Python's [built-in functions](http://docs.python.org/library/functions.html). `<child type="bool">True</child>` is the same as `child = bool(True)`.

# Adding items #

Adding items is as simple as adding tags inside `<Game>`.
```
<?xml version="1.0" encoding="UTF-8" ?>
<Game xmlns:items="pyf.items">
	...
	<items:Room name="Boring room"
		ldesc="This room is exceptionally boring.">

		<items:Item name="shelf" 
			adjective="wooden" 
			ldesc="It's a wooden shelf.">
		
			<items:Item name="pot"
				ldesc="It's a clay pot." />
			
		</items:Item>

	</items:Room>
</Game>
```
`xmlns:items` here imports `pyf.items` for use inside the script, so `items:Room` here is actually referring to the class `pyf.items.Room`. We could, of course, refer to a class in our own Python source, but often it's just quicker to use a standard class.

Like in the case of `<Game>`, all that happens here is that the class is instantiated and initiated with some values we defined - the only difference is some of the values are defined as tag attributes. Any tags contained in `<items:Room>` are also created and afterwards moved to the room, so the shelf will be in the boring room and the pot will be on the shelf.

For a list of default tags and attributes, see [Default Tags and Attributes](DefaultTagsAndAttributes.md).

# Using locals() #

As your game grows, you'll find it hard to update the dict you pass to `createFromScript`. You could write a function for automatically collecting any classes you want to use from the local namespace, which would be the best solution - as a quicker fix, however, you can call `locals()` to get a dict containing any definitions in the local namespace. You can pass this dict to `createFromScript` and it'll work pretty much like you expect. A word of caution though: the script will try to call any definition it encounters in the XML and the dict. If your source has a line `attr = "my string"` the script will try to call the string as soon as it encounters the line `<attr>`.
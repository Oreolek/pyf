While the PyF default library can handle most typical commands used in adventure games for you, you'll eventually run into a situation where you want to handle the user input in your own code. This article gives an overview of matching user input and writing output in PyF.

# The Handle Method #

A typical `handle` method looks like this:
```
def handle(self, sentence, output):
	if sentence == 'push *self':
		output.write("You poke the strange orb. It doesn't seem to react to touch.")
```

The `handle` method is invoked every time an object needs to handle user input. It's used to match input and write output accordingly - here the player is trying to push the strange orb, so we display a message saying it doesn't react to touch.

## Matching User Input ##

Matching a `sentence` can look a lot like matching any string, but the process underneath is slightly more complex. When the game lib parses user input into a `sentence` it's matched against every `Word` that has been defined in the game. Word is a simple string container that includes a word, its synonyms and some wildcards. A `Word` instance allows matches like the following:
```
>>> word = pyf.lib.Move('take', 'pick up', 'get')
>>> word == 'take'
True
>>> word == 'pick up'
True
>>> word == '*move'
True
>>> word == '*verb'
True
>>> print word
take
```
The list of wildcards is determined by the `Word` object's inheritance tree. `Move` is a subclass of `Touch`, which is a subclass of `Verb`. As such it matches any of the keywords `*move`, `*touch` and `*verb`. Some keywords like `*self`, which matches the object that's currently handling input, are added at runtime. All words also subclass `Word`, but `*word` isn't matched by any `Word` instance.

### The Sentence Object ###
A `Sentence` object is simply a container for `Word` objects. When it's matched against a string, the sentence will simply go through every word in the string and see if it equals its word in the same position.

```
>>> sentence == 'take magic wand'
True
>>> sentence == 'take wand'
True
>>> sentence == 'take the magic wand'
True
>>> sentence == '*verb *noun'
True
```

For more info on `Sentence` objects see [Sentences In Depth](Sentence.md).

## The Output Object ##
`Output` objects are used to write output for the user. `Output.write('Hello world!')` writes a string into the `output` and it's displayed as soon as the input handling is done. Although superficially it seems like your basic `print` command, it's different in many respects.

As soon as something is written to an `Output` it stops the input handling process and returns what has been written. This can be averted by adding `False` to the argument list, when you want to write multiple lines.
```
def handle(self, sentence, output):
	output.write("This is shown.", False)
	output.write("This too.")
	output.write("This is not.")
```
Typically this is used to write additional messages about what the player does - like display `(first standing up)` if the player does something that requires him to be standing. More importantly, however, it's used to tell the parser that the input has been succesfully handled and the standard response shouldn't be shown. Compare the following:
```
def handle(self, sentence, output):
	if sentence == 'eat *self'
		output.write("You munch down the delicious pie.", False)
		
...
> eat pie
You munch down the delicious pie.
The delicious pie is hardly edible.

----------------------------------------------------------------

def handle(self, sentence, output):
	if sentence == 'eat *self'
		output.write("You munch down the delicious pie.")
		
...
> eat pie
You munch down the delicious pie.
```
You can also add inline scripting to your output. For more info see [Inline Scripting](InlineScripting.md).
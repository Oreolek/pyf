PyF allows you to perform string replacement operations on your responses before they're displayed. Usually this is used for creating generic responses; for example to show a message like
```
You can't carry the shelf.
```
you would define the response as
```
You can't [verbs[0].name] [self.definite].
```
By default all text inside square brackets is treated as code, evaluated as an expression and added to the response. To display actual square brackets use `["["]something["]"]`.

There are a few useful variables that are available for inline scripts: first of all you can access the `sentence` object. This way you can get any word from the user input and use it to display a sensible response. You can use shorthands `verbs` and `nouns` to get a list of the words in the input respectively, and `actor` gets you the actor of the sentence. You can use `self` to access the object that's currently handling the input. Apart from those it's also possible to access the handling object's module with `module`, but this should be used with caution.

This kind of scripting is very powerful, but very easy to abuse. As a rule of thumb, never include code that affects the game world in inline scripts. And if your responses start resembling code more than prose, it's probably time to heavily rethink your approach. It's always easier, not to mention cleaner, to do
```
[self.getNewResponse()]
```
than
```
[module.Shelf.owner == module.Shed and 'some text' or 'other text']
```

NOTE: For PyF archives, `module` will be `__builtin__` rather than `__init__.py`.
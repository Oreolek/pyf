Properties are the standard way to add reusable functionality to an `Item`.

# Why use properties #

PyF allows you to define custom functionality for items relatively easily, but most objects don't need anything that's specific to your game. Properties implement many aspects of typical object behavior in adventure games, including closable and lockable containers, clothing, switches, buttons and even NPCs. And all those are available to you without writing a single line of code.

# Adding properties #

You can add properties in the class definition of your `Item` by definining `props` as a tuple containing `Property` instaces, or through a script by adding property classes inside your `Item` tag. In the first case you can customize the property's behavior by passing arguments to its constructor and in the latter you can use the `<attr>` tag.

If you need to add properties at runtime, you can use the `Item.addProp` method, but you should always call `Item.finalizeProps` after you're done adding them.

# Customizing property behavior #

The easiest way to customize property behavior is to change its attributes. Many properties define boolean switches that allow you to prevent an object from being used a certain way, like being dropped or sat on. A more powerful way is to add event listeners to the objects; not only does it allow you to stop unwanted behavior, but you can also make things happen in your game as a result. For a list of properties and their events, see [the list of standard properties](StandardProperties.md).

Beyond those approaches, you can also subclass any property and define custom handlers for them. Or you might even choose to write your own properties.

# The `pyf.properties` module #

PyF's standard property definitions are all accessible through `pyf.properties`, but their class definitions are split between different modules. For a list of PyF standard properties, see [the list of standard properties](StandardProperties.md).
This page lists some of the tags and attributes to available for different classes.

## `pyf.handler.Handler` ##

### tags: ###
| attr | Tags inside this tag are turned into values for this object's dict. Use attribute type to define the type of the value. If no type is specified, value will be treated as a string. Example: `<attr><age type="int">5</age></attr>`|
|:-----|:-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| response | Defines a standard response. Specify attribute `id` to assign it to the object's standard responses. `<response id="wait">You don't have time to wait.</response>` defined in an `Actor` instance will print `You don't have time to wait.` when the player waits. |

## `pyf.items.Item` ##

### attributes: ###
| name | A string specifying the name of this item. Separate multiple values with a comma (","). The first word will be its official name and the rest synonyms. |
|:-----|:--------------------------------------------------------------------------------------------------------------------------------------------------------|
| adjective | A string specifying the adjectives of this item. Separate multiple values with a comma (",").                                                           |
| ldesc | Turned into the item's long description.                                                                                                                |
| response | Defines a standard response. Specify attribute `sentence` to show a response to player input: `<response sentence="take *self">It's too heavy</response>` will print "It's too heavy" when player tries taking the `Item`. |

### tags: ###
| ldesc | Turned into the item's long description. |
|:------|:-----------------------------------------|

## `pyf.items.Room` ##

### tags: ###
| exits | Contains XML elements for each exit in this room. Node's content needs to be a string or a tag referring to a class. Example: `<exits><west><Cloakroom /></west></exits>` creates an exit to `Cloakroom`. |
|:------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
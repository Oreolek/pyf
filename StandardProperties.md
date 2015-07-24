For a more complete documentation, see the [API reference](APIReference.md).

# `pyf.props.general` #
Contains properties typical to most IF games.

## `Normal` ##
Used to display descriptions for objects.

**Events:**
  * _evtExamined_: Fired before the object's default description is shown. Listen to this if you want to display another message.


## `Mobile` ##
Defines item as something that can be moved around.

**Events:**
  * _evtTaken_: Fired before an actor takes object.
  * _evtDropped_: Fired before an actor drops object.

**Responses:**
  * _taken_: Displayed when player succesfully takes object.
  * _dropped_: Displayed when player succesfully drops object.
  * _alreadyTaken_: Displayed if player is trying to take something they're already carrying.
  * _alreadyDropped_: Displayed if player is trying to drop something they're not carrying.
  * _notTakeable_: Displayed when player tries to take object that's set as untakeable.
  * _notDroppable_: Displayed when player tries to drop object that's set as undroppable.
  * _pushed_: Displayed when player succesfully pushes object to another location within the room.
  * _alreadyPushed_: Displayed when object is already where player is trying to push it.
  * _notMovable_: Displayed when player tries to push object that's set as unmovable.

## `Openable` ##
Define object as something that can be opened and closed. If closed, actor can't interact with objects it contains.

**Events:**
  * _evtStateOpen_: Fired before object's `open` state changes.
  * _evtStateLocked_: Fired before object's `lockded` state changes.

**Responses:**
TODO

## `Dark` ##
Disallows handling objects contained, unless lit or the room contains a light source.

**Events:**
  * _evtStateLit_: Fired before object's `lit` state changes.

**Responses:**
TODO

## `LightSource` ##
Define item as something that can light a dark container.

**Events:**
None

**Responses:**
None

# `pyf.props.containers` #
TODO

# `pyf.props.functionality` #
TODO

# `pyf.props.characters` #
TODO

# `pyf.props.physical` #
TODO

# `pyf.props.technical` #
TODO
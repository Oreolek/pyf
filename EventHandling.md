# Adding event listeners #

An event listener is basically just a function that's called to handle an event. Event listeners should always be defined at the top level of your module; using anonymous functions or instance methods can make the object unpicklable.

You can use the `Handler.addEventListener` method to add event listeners to your objects. It takes 2 arguments: ID, usually a string, identifying the event you want to listen to and a tuple ending in your handler function, preceded by the arguments you want to pass to it.

```
self.addEventListener('evtStateWorn', (self, "You can't wear the cape.", capeWorn))
```
This will call `capeWorn` with the arguments `self` and `"You can't wear the cape."` every time `evtStateWorn` is fired.
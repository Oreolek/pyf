PyF archive is a simple zip-file with some naming conventions, which aims to be the standard way to distribute PyF games. The only restriction is that the main entry point needs to be in a file called `__init__.py` and that its `Game` object can be accessed through a variable called `game`.

## Current challenges ##

  * Find a way to import games with `zipimporter` in a sandboxed environment.
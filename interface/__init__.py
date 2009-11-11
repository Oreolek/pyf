
"""This file is part of PyF.

PyF is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

PyF is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with PyF.  If not, see <http://www.gnu.org/licenses/>.
"""

from pyf import states

def runGame(game):
	'''Very basic command line interface for playing PyF games. "Quit" exits the game.'''
	
	print 'Type "quit" at any time to quit the game.'
	interface = TerminalInterface(game)
	interface.output(game.getIntro())
	while game.state != states.Finished: # While the game is running
		input = raw_input('> ') # Get user input
		if input == 'quit': 
			break # Exit game 
		interface.input(input) # Pass player input to the game and print the output
		
import cgi, re
		
class TerminalInterface:
	replace = {'<br />': "\n", '<br/>':"\n", '<b>': '-- ', '</b>': ' --'}
	def __init__(self, game):
		self.game = game

	def input(self, s):
		self.output(self.game.input(s))
		
			
	def cleanOutput(self, s):
		p = re.compile(r'<.*?>')
	    
		for tag in self.replace:
			s = s.replace(tag, self.replace[tag])
		return p.sub('', s)
		
	def output(self, output):
		for line in output.lines:
			print self.cleanOutput(line)
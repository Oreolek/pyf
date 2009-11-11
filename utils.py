'''Utility functions.'''

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

def naturalJoin(l, glue, lastglue):
	'''Join list of strings using glue and lastglue. Join last 2 items with lastglue
	and the rest with glue. Returns empty string if l empty.
	
	l : list
	glue : str
	lastglue : str
	
	returns : str'''
	if len(l) == 0:
		return ''
	lfirst, llast = l[:-2], l[-2:]
	s = lastglue.join(llast)
	s = glue.join(lfirst+[s])

	return s
	
def makeTuple(other):
	'''If other is of type list, turn list into a tuple. Str or unicode is turned into 
	a tuple with one item. If can't turn into tuple, raise TypeError.'''
	if type(other) == list:
		return tuple(other)
	elif type(other) == str or type(other) == str:
		return (other,)
	elif type(other) == tuple:
		return other
		
	raise TypeError("Can't cast type %s into a tuple." % type(other))
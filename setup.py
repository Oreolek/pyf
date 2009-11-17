
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

from distutils.core import setup
setup(name="pyf",
	version="0.6b",
	description="Python IF library",
	url="http://pyf.sourceforge.net/",
	packages=['pyf','pyf.interface', 'pyf.props'],
	maintainer="Tuomas Kanerva",
	maintainer_email="tuomas.kanerva@gmail.com"
	)
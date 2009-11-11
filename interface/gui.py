"""Very basic GUI for running PyF formatted zip files."""

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

import wx, wx.html, pyf

class GameWindow(wx.Frame):
	ID_CLOSE_WINDOW = 300
	
	def __init__(self, parent, id):
		wx.Frame.__init__(self, parent, id, size=(400, 700))
		
		self.html = HTMLDisplay(self)
		self.input = TextInput(self)
		self.button = wx.Button(self, label='')
		
		self.Connect(self.input.GetId(), wx.ID_ANY, wx.wxEVT_COMMAND_TEXT_ENTER, self.newLine)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.lowSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.lowSizer.Add(self.button,flag=wx.EXPAND, proportion=0)
		self.lowSizer.Add(self.input,flag=wx.EXPAND, proportion=1)
		
		self.sizer.Add(self.html,1,wx.EXPAND)
		self.sizer.Add(self.lowSizer, flag=wx.EXPAND, proportion=0)
		
		self.SetSizer(self.sizer)
		self.SetAutoLayout(1)
		
		self.Centre()
		
		m = GameMenuBar()
		wx.EVT_MENU(self, m.CHANGE_FONT, lambda event: self.html.setFont())
		self.SetMenuBar(m)
		
		self.Show(True)
		self.input.SetFocus()
		
	def onClose(self, event):
		self.Close()
		
	def showLine(self):
		if self.html.nextLine():
			self.input.Enable()
			self.input.SetFocus()
			self.input.Clear()
		else:
			self.input.Disable()
			self.html.SetFocus()

			self.html.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
			self.input.SetValue('[More]')
			
	def onKeyDown(self, event):
		self.showLine()
		
	def newLine(self, event):
		string = self.input.newLine()
		string = string.encode()
		
		self.html.appendLines(['<p>' + self.game.state.request +' '+ string + '</p>'] + self.game.input(string).lines)
		self.showLine()
		
		self.button.SetLabel(self.game.state.request)
		
		if self.game.state == pyf.states.Finished:
			self.input.Disable()
		
	def initGame(self):
		self.html.SetPage('')
		self.input.Clear()
		
		# show initial description
		o = self.game.getIntro()
		self.html.appendLines(o.lines)
		self.showLine()
		
		self.SetTitle(self.game.name)
		
		self.button.SetLabel(self.game.state.request)
		self.input.Enable()
		
	def loadGame(self, name):
		from pyf.interface.package import Importer
		
		self.zip = Importer(name)
		self.game = self.zip.game()
		
class TextInput(wx.TextCtrl):
	def __init__(self, parent):
		wx.TextCtrl.__init__(self, parent, style=wx.TE_PROCESS_ENTER)
		
	def newLine(self):
		s = self.GetLineText(0)
		self.Clear()
		return s
		
class HTMLDisplay(wx.html.HtmlWindow):
	buffer = []
	def __init__(self, parent):
		wx.html.HtmlWindow.__init__(self, parent)
		self.paused = False
		
	def appendLines(self, lines):
		s = '<p>' + '</p><p>'.join(lines) + '</p>'
		self.append(s)
			
	def append(self, s):
		self.buffer.extend(s.split('<pause/>'))
		
	def nextLine(self):
		if buffer == []:
			raise Exception("Buffer empty")
		else:
			pos = self.GetScrollPos(wx.VERTICAL)
			size = self.size()
			self.Freeze()
			
			s = self.buffer[0]
			del self.buffer[0]
			self.AppendToPage(s)
			
			isDown = self.scrollDown(pos,size)
			self.Thaw()

			return isDown

			
	def bufferEmpty(self): return self.buffer == []
	
	def setFont(self):
		f = wx.FontData()
		dialog = wx.FontDialog(self.GetParent(), f)

		if dialog.ShowModal() == wx.ID_OK:
			self.SetFonts(dialog.GetFontData())
		
	def scrollDown(self, pos, size):
		self.Scroll(-1, pos + size)
		
		if self.bufferEmpty():
			if pos == 0 or size == 0:
				return True
			return self.scrolledDown()
		else:
			return False
				
	def scrolledDown(self):
		return self.GetScrollPos(wx.VERTICAL) + self.size() == self.GetScrollRange(wx.VERTICAL)
		
	def size(self): return self.GetClientSize()[1] / self.GetScrollPixelsPerUnit()[1]
		
	def appendLine(self, line):
		self.append('<p>' + line + '</p>')
		
	def onKeyPress(self, event):
		self.unPause()
		
class FontWindow(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)
		pass
		
class GameMenuBar(wx.MenuBar):
	CHANGE_FONT = wx.NewId()

	def __init__(self, *args, **kwargs):
		wx.MenuBar.__init__(self, *args, **kwargs)
 		self.edit = wx.Menu()
		self.Append(self.edit, '&Edit')
		self.edit.Append(self.CHANGE_FONT, 'Change game font')

def runGame(gameFile):
	'''gameFile : ZipFile'''
	app = wx.PySimpleApp()
	gameWindow = GameWindow(None, wx.ID_ANY)
	gameWindow.loadGame(gameFile)
	gameWindow.initGame()
	app.MainLoop()
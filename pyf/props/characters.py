'''Defines characters.'''

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
from pyf.props import Property
from pyf import states

class NPC(Property):
	'''Defines item as something that you can have a conversation with.'''
	
	EVT_CONVERSATION_STARTED = "evtConversationStarted"
	'''Fired every time the player starts a conversation with NPC. Not fired when answering
	questions outside a conversation.'''
	EVT_CONVERSATION_ENDED = "evtConversationEnded"
	'''Fired every time the player ends a conversation with NPC. Not fired when answering
	questions outside a conversation.'''
	
	conversationState = states.Talking
	'''State to use for conversation.'''
	
	CONVERSATION_STARTED = 'conversationStarted'
	CONVERSATION_ENDED = "conversationEnded"
	
	UNKNOWN_TOPIC = 'unknownTopic'
	UNKNOWN_ORDER = 'unknownOrder'
	UNKNOWN_QUESTION = 'unknownQuestion'
	HELP = 'help'
	
	ANSWERED = "answered"
	
	ENDING = "end"
	
	responses = {
		CONVERSATION_STARTED:'"Yes?"',
		CONVERSATION_ENDED:'You end the conversation.',
		HELP:'(type topics you want to talk about - type "end" to end the conversation)',
		UNKNOWN_TOPIC : "\"I don't know anything about that.\"",
		UNKNOWN_ORDER : "\"I'm not going to do that.\"",
		UNKNOWN_QUESTION : "\"I don't know anything about that.\""
	}
	
	def __init__(self, topics={}, answers={}, orders={}):
		Property.__init__(self)
		self.topics = topics
		'''Dict containing topics you can tell this NPC about.'''
		self.answers = answers
		'''Dict containing topics you can ask this NPC about.'''
		self.orders = orders
		'''Dict containing topics can ask this NPC to do.'''
		
	def handle(self, sentence, output):
		s = sentence[:3]
		
		if sentence == ('talk to', '*self'):
			self.initConversation()
			self.write(output, self.HELP, False)
			self.write(output, self.CONVERSATION_STARTED)
			
		elif s == ('talk to', '*self', 'about'):
			self.askAbout(sentence[3:], output)
			self.tellAbout(sentence[3:], output)
			self.write(output, self.UNKNOWN_TOPIC)
		elif s == ('ask', '*self', 'about'):
			self.askAbout(sentence[3:], output)
			self.write(output, self.UNKNOWN_QUESTION)
		elif s == ('tell', '*self', 'about'):
			self.tellAbout(sentence[3:], output)
			self.write(output, self.UNKNOWN_TOPIC)
		elif s == ('tell', '*self', 'to') or s == ('ask', '*self', 'to'):
			self.orderTo(sentence[3:], output)
			self.write(output, self.UNKNOWN_ORDER)
			
	def answerFromDict(self, sentence, dict):
		for t in dict:
			for topic in t.split('/'):
				if topic == sentence:
					return dict[t]
		
	def askAbout(self, sentence, output):
		s = self.answerFromDict(sentence, self.answers)
		if s:
			output.write(s, obj=self.owner)

	def tellAbout(self, sentence, output):
		s = self.answerFromDict(sentence, self.topics)
		if s:
			output.write(s, obj=self.owner)
				
	def orderTo(self, sentence, output):
		s = self.answerFromDict(sentence, self.orders)
		if s:
			output.write(s, obj=self.owner)
		
	def converseAbout(self, sentence, output):
		self.askAbout(sentence, output)
		self.tellAbout(sentence, output)

	def initConversation(self):
		self.dispatchEvent(NPC.EVT_CONVERSATION_STARTED)
		self.ownerGame.actor.state = self.conversationState(self.ownerGame.actor, self)
		
	def endConversation(self):
		self.dispatchEvent(NPC.EVT_CONVERSATION_ENDED)
		
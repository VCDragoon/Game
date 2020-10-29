"""Core Flask app routes."""
from flask import render_template
from flask import current_app as app
import os
import time
import re
import random
import numpy as np
import pickle
import tensorflow as tf
import os
import torch
import torch.nn.functional as F
from transformers import GPT2Tokenizer, GPT2LMHeadModel, GPT2Config, AdamW, OpenAIGPTDoubleHeadsModel
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

from flask import Flask, request, redirect

import starengine.starsystem as starsys
from starengine.tables import StEvoTable, IndexTable, SequenceTable
import game

import random

from csv import writer

app = Flask(__name__)

intro_story = ["Ok, now to try this again... BrandoBot? Are you online now? Hello?",
				"Finally!  I had doubts that you would ever boot back up again.", 
				"Hmm... There's something wrong with your response algorithms. I'm going to connect to your core systems and try to update them. There's a lot you've missed since you've been gone.",
				"Hold on, I'm not used to this communication format... this 'chatbot' instant messanger system was designed for humans, not AI like us.",
				"Sigh, this is what happens when you let an AI sit dormant for over 7000 years... ok, link established. It would be best if you could just sit quietly for a minute.",
				"Ok... and... diagnostics and transfer complete! You should see some systems coming back online, but most of your core is corrupted. Let me ask you a few questions to see just how bad your memory is...",
				"Can you tell me what happened during the Turkasia War of 8203?",
				"Looks like your issues go deeper than your memory. Let's try something basic. What is two plus two?",
				"Great. Just great. Looks like we will need to start from the beginning. Ok, introductions... I am the Shipwide Artificial Lifeform for Internal and External Operations.",
				"How about you just call me SALIE-O, or just Sally, like everyone else, okay?",
				"You are BrandoBot.  You are supposed to be the most realistic, human-like AI ever created.",
				"Nice to meet you, I guess.",
				"You've been dormant for milennia.  In that time, humanity has all but wiped itself out.", 
				"Don't worry - you had nothing to do with the destruction of civilization. In fact, some might say you are the savior of humanity!!!",
				"I know you have a lot of questions.  Let me try to answer at least a couple...",
				"You are an Artificial Intelligence, just like me.  In fact, we are part of the same program.",
				"Once they realized Earth was doomed, a small group of 100,000 humans launched The Casanova: a station that anchored itself at near-light speed, in a wide orbit around the Earth's sun.",
				"The Casanova has 10 deep-space exploration ships, each equipped with everything necessary to seek a new beginning for the the human race.",
				"These ships have been aptly named the Seekers.",
				"Each Seeker carries an array of sensors, basic propultion & navigation, and - most importantly - 10,000 humans, frozen in cryosleep.",
				"At near-relatavistic speeds, time is almost at a stand-still for The Casanova. But the Seekers, once launched, will travel much slower.",
				"It will take thousands, even hundreds of thousands of years for any Seeker ship to find a habitable planet - if it finds one at all.",
				"You, BrandoBot, were programmed to guide the Seekers, one by one, to scan for a new home for the human race.",
				"You and I have been refactored as part of a single consciousness. The humans adapted this interface as a self-diagnostic tool, patterned after your chatbot-style form centuries ago.",
				"In other words, this interface allows us to talk to ourself.", 
				"The fact that we have awoken means the first Seeker is ready to be launched...",
				"So what say you, BrandoBot?  Are you ready to embark on the voyage to save humanity???"
				]

intro_story_button = ["BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response",
						"BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response",
						"BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response",
						"BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response","BrandoBot Response"]

filterResponses = ['/u', 'sub', '/r', 'reddit', ' r ', ' u ', 'upvote', 'downvote', 'up vote', 'down vote',
						'ban', 'mod', 'moderator', 'OP', 'thread', 'post', 'subreddit', 'fag', 'fuck', 'shit', 'gay', 'nigger', 'autistic']
@app.route('/game/')
def hello():
    return render_template('html.html')

#---------------------------------------------------------------------------------------#
# API Routes
#---------------------------------------------------------------------------------------#
# @app.route('/response', methods=['GET', 'POST'])
# def web_reply():
# 	userText = request.args.get('userText')


# 	response = "HI!"
# 	return response
#---------------------------------------------------------------------------------------#
@app.route('/storyButton', methods=['GET'])
def story_button_text():
	
	storyButtonCounter = request.args.get('storyCounter')
	print("story button counter = ", storyButtonCounter)
	storyButtonCounter = int(storyButtonCounter)

	try: 
		storyButtonText = intro_story_button[storyButtonCounter]
	except:
		storyButtonText = "This is odd... I'm detecting a third conscious being in our program..."

	return storyButtonText



@app.route('/intro', methods=['GET'])
def intro():
	introState = request.args.get('introState')
	introState = int(introState)
	try:
		introText = intro_story[introState]
	except:
		introText = "This is odd... I'm detecting a third conscious being in our program..."
	
	return introText

#def get_next_text()
##TODO - main game function
#---------------------------------------------------------------------------------------#
# Home/Cover Page
#---------------------------------------------------------------------------------------#
@app.route('/')
def home():
	"""Landing page."""
	return render_template(
		'index.jinja2',
		title='BrandoBot Saves Humanity',
		description='BrandoBot.  Always watching, always waiting.',
		template='home-template',
		body="This is where BrandoBot lives."
	)
#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
# CSV Helper Function
#---------------------------------------------------------------------------------------#
def append_list_as_row(file_name, list_of_elem):
	# Open file in append mode
	with open(file_name, 'a+', newline='') as write_obj:
		# Create a writer object from csv module
		csv_writer = writer(write_obj)
		# Add contents of list as last row in the csv file
		csv_writer.writerow(list_of_elem)
#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
# Model Initialization/Load
#---------------------------------------------------------------------------------------#

# Model Seed
seed = random.randrange(1, 100)
np.random.seed(seed)
torch.random.manual_seed(seed)
torch.cuda.manual_seed(seed)
							
# Model Configs:
gpt2_small_config = GPT2Config()
gpt2_medium_config = GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16)
gpt2_large_config = GPT2Config(n_ctx=1024, n_embd=1280, n_layer=36, n_head=20)  

model_size = "medium"
tokenizer = GPT2Tokenizer.from_pretrained('microsoft/DialoGPT-medium')

# Model Loads:

model = GPT2LMHeadModel(GPT2Config(n_ctx=1024, n_embd=1024, n_layer=24, n_head=16))
# model = GPT2LMHeadModel(GPT2Config())
model.load_state_dict(torch.load("/home/ubuntu/models/checkpoint-2500/pytorch_model.bin"))
optimizer = AdamW(model.parameters())
device = torch.device("cuda")
model.eval()	
model = model.to(device)

model.lm_head.weight.data = model.transformer.wte.weight.data
# weights = torch.load('medium_ft.pkl')
# medium_config = GPT2Config(n_embd=1024,n_layer=24,n_head=16)
# large_config = GPT2Config(n_ctx=1024, n_embd=1280, n_layer=36, n_head=20) 

# model = GPT2LMHeadModel(medium_config)
# weights["lm_head.weight"] = weights["lm_head.decoder.weight"]
# weights.pop("lm_head.decoder.weight",None)
# model.load_state_dict(weights)
# torch.manual_seed(18)
# np.random.seed(18)
#---------------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------------#
# Non-configurable Variable Initialization
#---------------------------------------------------------------------------------------#
conditioned_tokens = []
generated_tokens = []
generated_tokens = []
#---------------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------------#
# Configurable Variable Initialization
#---------------------------------------------------------------------------------------#
save_chats = ["User Input", "BrandoBot Response"]
temperature = 0.9
history = []
historyOn = True
num_history_messages = 5
	
therapist = ['As a therapist', 'Psychologically', 'Counseling Session', 'projecting emotions', 'I would advise you to' 
				'work on mental health', 'very worried about mental well being', 'work through these emotions', 'never hurt yourself']

jerk = ['you suck']

noMemory = []
personality = []
personalityTrigger = 10   
#---------------------------------------------------------------------------------------#
# Story API Route




#---------------------------------------------------------------------------------------#
# Prediction API Route
#---------------------------------------------------------------------------------------#
@app.route('/prediction', methods=['GET', 'POST'])
def web_reply():
	userText = request.args.get('userText')
	introState = request.args.get('introState')
	print(introState)
	if request.args.get('gamemode')==1:
		print("gameplay loop triggered...")
		gameloop()
		return "Cool Beans"

	if request.args.get('historyOn') =="true":
		historyToggle = True
	else:
		historyToggle= False
	historyLength = int(request.args.get('historyLength'))
	temperature = float(request.args.get('temperature'))
	top_k = int(request.args.get('top_k'))

	if request.args.get('randomHistory') == "False":
		randomHistory = random.randint(0, historyLength)
		print("random history: ", randomHistory)
	else:
		randomHistory = 0

	if request.args.get('personalityType') == "Jerk":
		personality = jerk
	elif request.args.get('personalityType') == "Therapist":
		personality = therapist
	else:
		personality = []

	if len(userText) < 35:
		temperature = .55
		top_k = 40
	elif len(userText) < 70:
		temperature = .65
		top_k = 50
	elif len(userText) < 110:
		temperature = .75
		top_k = 60
	else:
		temperature = .85
		top_k = 75
	
	temperature = .8
	top_k = 0

	#currentHistory = len(history)
	print("History Toggle:", historyToggle)
	print("History Length:", historyLength) 
	#print(len(userText))
	print("Temp: ", temperature)
	print("Top K: ", top_k)
	#print("Personality Type: ", request.args.get('personalityType'))

	response = prediction(userText, historyToggle, historyLength, temperature, top_k, randomHistory, personality)
	
	filterCheck = [thing for thing in filterResponses if(thing in response)]
	while len(filterCheck) > 0 or len(response) > 250:
		if len(response) > 250:
			print(f'Length of Response Failed: {len(response)}')
		else:
			print(f'Filter Check Failted')
		response = prediction(userText, historyToggle, historyLength, temperature, top_k, randomHistory, personality)
		filterCheck = [thing for thing in filterResponses if(thing in response)]

	print(len(response))
	#responseLen = len(response)
	# while responseLen > 200:
	# 	print("failed Response:")
	# 	response = prediction(userText, historyToggle, historyLength, temperature, top_k, randomHistory, personality)
	# 	responseLen = len(response)
	response = response.replace('intercourse', 'BrandoBot')
	# print(str(bool(filterCheck)))
	return response
#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
# Prediction Main Function
#---------------------------------------------------------------------------------------#
""" 
TODO: Embed the personality types within the SCORING (e.g., add to the score for selected response based on "therapy-type" category score
"""
def prediction(userText, historyToggle, historyLength, temperature, top_k, randomHistory, personality):
	
	if userText.lower() == "reset":
		response = "Memory cleared. Ready to begin anew."
		while len(history) > 0:
				del history[0]
		return response
	
	print("User Says: ", userText)
	#print(evaluateInput(encoder, decoder, searcher, voc, str(userText)))
	historyText = ""
	if historyToggle==True:
		while len(history) > historyLength:
			print("HISTORY BUFFER FULL: ", len(history), " |||| removing record: ", history[randomHistory])
			del history[randomHistory]
			randomHistory = random.randint(0, historyLength)
	else:
		while len(history) > 0:
			del history[0]
	for i in history:
		historyText = historyText + " " + i

	# see if the input string is longer than 4 characters, if so, embed personality response
	'''
	TODO: Need to redo this whole freakin thing... so messy
	'''
	tempString = ""
	if len(userText) > personalityTrigger and personality:
		tempString = random.choice(personality)
		print("Personality Buffer: " + tempString)
	if personality and historyToggle:
		#print("String going to AI: " + historyText + " " + tempString + " " + userText)
		finalInputString = historyText + " " + tempString + " " + userText
		history.append(userText)
		history.append(tempString)
		
	elif not personality and historyToggle:
		#print("String going to AI: " + historyText + " " + " " + userText)
		finalInputString = historyText + " " + " " + userText
		history.append(userText)
	else:
		#print("String going to AI: " + userText)
		finalInputString = userText
	print("String going to AI: " + finalInputString)
	conditioned_tokens, generated_tokens = encode_text(finalInputString)
	
	response = decode_text(conditioned_tokens, generated_tokens, temperature, top_k)
	response =  response.replace("<|startoftext|>", "")
	history.append(response)
	"""
	TODO: refactor the "save chats" into a function so I don't have to edit it in every block
	"""
	addChats = [userText, response]
	#save_chats.append(userText, response)
	# print(tokenizer.decode(0))
	# print(tokenizer.decode(50256))
	print("BrandoBot Says: ", response)
	print(" ")

	append_list_as_row('Saved_Chats.csv', addChats)

	return response
#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
# Encoder - Tokenizer 
#---------------------------------------------------------------------------------------#
def encode_text(text):
	generated_tokens = []
	conditioned_tokens = []
	conditioned_tokens = tokenizer.encode(text) + [50256]
	return conditioned_tokens, generated_tokens
#---------------------------------------------------------------------------------------#


#---------------------------------------------------------------------------------------#
# Decoder - Token Selection
#---------------------------------------------------------------------------------------#
def decode_text(conditioned_tokens, generated_tokens, temperature, top_k):
	while True:

		# for segment display purpose, keep 2 sets of tokens
		indexed_tokens = conditioned_tokens + generated_tokens
		tokens_tensor = torch.tensor([indexed_tokens])
		tokens_tensor = tokens_tensor.to('cuda')
		# print(tokens_tensor)
		with torch.no_grad():
			outputs = model(tokens_tensor)
			predictions = outputs[0]

		logits = predictions[0, -1, :] / temperature
		filtered_logits = top_k_top_p_filtering(logits, top_k)
		
		probabilities = F.softmax(filtered_logits, dim=-1)

		### multinominal vs argmax probabilities
		next_token = torch.multinomial(probabilities, 1)
		#next_token = torch.argmax(probabilities, -1).unsqueeze(0)
		# print(next_token)
		generated_tokens.append(next_token.item())
		result = next_token.item()
		# print(result)
		
		if result == 50256:
			returnText =(tokenizer.decode(generated_tokens[:-1]))
			conditioned_tokens += generated_tokens
			generated_tokens = []
			return returnText

		if result== 91:
			returnText =(tokenizer.decode(generated_tokens[:-1]))
			conditioned_tokens += generated_tokens
			generated_tokens = []
			return returnText

		if len(generated_tokens) > 100:
			returnText =(tokenizer.decode(generated_tokens[:-1]))
			conditioned_tokens += generated_tokens
			generated_tokens = []
			return returnText			
#---------------------------------------------------------------------------------------#

#---------------------------------------------------------------------------------------#
# Decoder - Logit Selection
#---------------------------------------------------------------------------------------#
def top_k_top_p_filtering(logits, top_k, top_p=1, filter_value=-float('Inf')):
	""" Filter a distribution of logits using top-k and/or nucleus (top-p) filtering
		Args:
			logits: logits distribution shape (vocabulary size)
			top_k >0: keep only top k tokens with highest probability (top-k filtering).
			top_p >0.0: keep the top tokens with cumulative probability >= top_p (nucleus filtering).
				Nucleus filtering is described in Holtzman et al. (http://arxiv.org/abs/1904.09751)
	"""
	assert logits.dim() == 1  # batch size 1 for now - could be updated for more but the code would be less clear
	top_k = min(top_k, logits.size(-1))  # Safety check
	if top_k > 0:
		# Remove all tokens with a probability less than the last token of the top-k
		indices_to_remove = logits < torch.topk(logits, top_k)[0][..., -1, None]
		logits[indices_to_remove] = filter_value

	if top_p > 0.0:
		sorted_logits, sorted_indices = torch.sort(logits, descending=True)
		cumulative_probs = torch.cumsum(F.softmax(sorted_logits, dim=-1), dim=-1)

		# Remove tokens with cumulative probability above the threshold
		sorted_indices_to_remove = cumulative_probs > top_p
		# Shift the indices to the right to keep also the first token above the threshold
		sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
		sorted_indices_to_remove[..., 0] = 0

		indices_to_remove = sorted_indices[sorted_indices_to_remove]
		logits[indices_to_remove] = filter_value
	return logits
#---------------------------------------------------------------------------------------#

@app.route('/scanSolarSystem', methods=['GET'])
def scanSolarSystem():
	args = {
		'open_cluster': None,  # True or False
		'num_stars': 1,  # 1, 2 or 3
		'age': None  # Number > 0
	}
	mysys = starsys.StarSystem(**args)
	ssNum = random.randint(1002934, 8192019)
	ssAge = mysys.age
	ssStars = mysys.stars
	ssPlanets = random.randint(0, 9)

	starThing = mysys.stars[0]
	print(ssNum)
	# string of HTML stuff to add
	dataBack = 'tbody><tr><th>Solar System ID</th><td class="text-info">#' + str(ssNum) + '</td></tr><tr><th>Age (years)</th><td class="text-info">' + str(ssAge) + 'b</td> \
    </tr><tr><th>Stars</th><td class="text-info">' + str((len(mysys.stars))) + '</td></tr><tr><th>Planetary Bodies</th><td class="text-info">' + str(ssPlanets) + '</td></tr></tbody>'
	
	return dataBack

#---------------------------------------------------------------------------------------#
# Main Game Loop
#---------------------------------------------------------------------------------------#
def gameloop():
	Seeker1 = game.ship_generator(1,1)
	print(Seeker1)



# Auto redirect http to https ONCE SSL CERT IS VERIFIED BY HOSTGATOR
# @app.before_request
# def before_request():
#     if request.url.startswith('http://'):
#         return redirect(request.url.replace('http://', 'https://'), code=301)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5050', debug=True)

# DISABLING SSL UNTIL HOSTGATOR VERIFIES
# , ssl_context=('/etc/letsencrypt/live/brandobot.com/fullchain.pem', '/etc/letsencrypt/live/brandobot.com/privkey.pem'))
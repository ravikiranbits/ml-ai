from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from rasa_core.actions.action import Action
from rasa_core.events import SlotSet
from rasa_core.events import Restarted
from collections import OrderedDict
import zomatopy
import json
import re
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
import pandas as pd


from zomato_slots import results
from city_check import check_location
from email_config import Config
from flask_mail_check import send_email

class ActionValidateLocation(Action):
	def name(self):
		return 'action_validate_location'
		
	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		check = check_location(loc)

		if check is not None:
			if check == 'found':
				return[SlotSet('location', loc)]
			else:
				dispatcher.utter_message("Sorry we do not operate in this location yet. Please try some other location.")
				return[SlotSet('location', None)]
		else:
			dispatcher.utter_message("Sorry I could not understand the location you provided. Pleast try some other location.")
			return[SlotSet('location', None)]
		
		return [SlotSet('location',check['location_new']), SlotSet('location_found',check['location_f'])]

class ActionValidateCuisine(Action):
	def name(self):
		return 'action_validate_cuisine'
		
	def run(self, dispatcher, tracker, domain):
		list_cuisine = ["chinese","mexican","american","italian","south indian","north indian"]
		cuisine = tracker.get_slot('cuisine')
		print("cuisine entered is: ", cuisine)
		if cuisine is not None:
			if cuisine.lower() in list_cuisine:
				return[SlotSet('cuisine',cuisine)]
			else:
				dispatcher.utter_message("Sorry this is not a valid cuisine. please check for typing errors")
				return[SlotSet('cuisine',None)]
		else:
			dispatcher.utter_message("Sorry I could not understand the cuisine name you provided")
			return[SlotSet('cuisine', None)]			
	
class ActionValidateBudget(Action):
	def name(self):
		return 'action_validate_budget'
		
	def run(self, dispatcher, tracker, domain):
		cost_queried = tracker.get_slot('budget')
		if cost_queried == 'less than 300' or cost_queried == 'lesser than 300' or cost_queried == 'lower than 300' or cost_queried == '< 300' or cost_queried == '<300'or ("cheap" in cost_queried):
			print('low budget selected')
			return[SlotSet('budget', 'low')]
		elif cost_queried == 'more than 700' or cost_queried == 'greater than 700' or cost_queried == 'higher than 700' or cost_queried == '> 700' or cost_queried == '>700' or ("costly" in cost_queried) or ("expensive" in cost_queried):
			print('high budget selected')
			return[SlotSet('budget', 'high')]
		else:
			print('mid budget selected')
			return[SlotSet('budget', 'mid')] #always return mid budget by default
	
class ActionSearchRestaurants(Action):
	def name(self):
		return 'action_restaurant'
		
	def run(self, dispatcher, tracker, domain):
		loc = tracker.get_slot('location')
		cuisine = tracker.get_slot('cuisine')
		price = tracker.get_slot('budget')

		global restaurants

		restaurants = results(loc, cuisine, price)
		top5 = restaurants.head(5) 
		
		# top 5 results to display
		if len(top5)>0:
			response = 'Showing you top results:' + "\n"
			for index, row in top5.iterrows():
				response = response + str(row["restaurant_name"]) + ' in ' + row['restaurant_address'] + ' has been rated ' + str(row['restaurant_rating'])+"\n"
			
			dispatcher.utter_message(str(response))
			return [SlotSet('budget',price)]

		else:
			response = 'No restaurants found' 
			dispatcher.utter_message(str(response))
			return [SlotSet('location',None), SlotSet('cuisine',None), SlotSet('budget',None)]

		# dispatcher.utter_message(str(response))
		# return [SlotSet('budget',price)]


class ActionValidateEmail(Action):
	def name(self):
		return 'action_validate_email'
		
	def run(self, dispatcher, tracker, domain):
		email_check = tracker.get_slot('email')
		if email_check is not None:
			if re.search("(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",email_check):
				return[SlotSet('email',email_check)]
			else:
				dispatcher.utter_message("Sorry this is not a valid email. Please give a valid email.")
				return[SlotSet('email',None)]
		else:
			dispatcher.utter_message("Sorry I could not understand the email address which you provided. Please provide again.")
			return[SlotSet('email', None)]			

class ActionSendEmail(Action):
	def name(self):
		return 'action_email'
		
	def run(self, dispatcher, tracker, domain):
		recipient = tracker.get_slot('email')

		top10 = restaurants.head(10)
		print("email is {}".format(recipient))
		send_email(recipient, top10)

		dispatcher.utter_message("Have a great day!")
		
class ActionRestarted(Action): 	
    def name(self): 		
        return 'action_restarted' 	
    def run(self, dispatcher, tracker, domain): 
        return[Restarted()] 

import tweepy, json, datetime, os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

# Parameters:
#   Words to filter tweets by:
words_search = ["covid", "coronavirus"]
#   Maximum of countries showed in plot
max_of_countries_in_plot = 10
#   Number of minutes after erasing old tweets
minutes_erasing = 10

# Definition of class for data streaming from Twitter
class MyTweetListener(tweepy.StreamListener):

	# Class dataframes for data received
	df = pd.DataFrame(columns=["Text", "Country", "Country Code", "Date"])
	dfByCountry = pd.DataFrame()

	# Init figure
	fig = plt.figure()
	axes= fig.add_axes()
	plt.ion()
	plt.gcf().set_size_inches(10.5, 7.5, forward=True)

	# Update plot
	def update_plot2(self):
		x = self.dfByCountry["No of Tweets"].index[:max_of_countries_in_plot]
		y = self.dfByCountry["No of Tweets"].head(max_of_countries_in_plot)
		plt.clf()
		plt.bar(x, y)
		plt.xticks(x, rotation=20, size=10)
		plt.draw()
		plt.title("Geo located tweets filtered by word ''"+words_search[0]+ \
			"'' by country in the last "+str(minutes_erasing)+" minutes")
		plt.pause(0.5)

	# Print if connection has been made with API
	def on_connect(self):
		print("Connected to Twitter API.")
		self.df = pd.DataFrame(columns=["Text", "Country", "Country Code", "Date"])

	# Method called every time an update is received
	def on_status(self, status):
		if type(status.place) != type(None):

			# Add new tweets
			self.df = self.df.append({"Text": status.text, 
							"Country": status.place.country,
							"Country Code": status.place.country_code,
							"Date": status.created_at,
							"No of Tweets": 1},
							ignore_index=True)

			# Drop old tweets
			current_time = datetime.datetime.utcnow()
			self.df = self.df[self.df["Date"] > current_time - datetime.timedelta(seconds=minutes_erasing*60)]

			self.dfByCountry = self.df.groupby("Country").sum().sort_values(by="No of Tweets", ascending=False)

			os.system('cls')
			print(self.dfByCountry.head())
			print(self.df[["Text", "Country"]].tail())
			self.update_plot2()

	# Print error
	def on_error(self, status_code):
		print("Error: ", status_code)


# Keys and passwords for authentication
# Add your keys and token from your application from Twitter Dev
consumer_key = ""
consumer_secret = ""
access_token = ""
access_token_secret = ""

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

# API instance
api = tweepy.API(auth, wait_on_rate_limit=True,
				 wait_on_rate_limit_notify=True)

# Listener instance
stream = MyTweetListener()
streamingAPI = tweepy.Stream(auth=api.auth, listener=stream)

# This method acts as the main loop
streamingAPI.filter(track=words_search)

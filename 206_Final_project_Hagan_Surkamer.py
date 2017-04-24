###### INSTRUCTIONS

# An outline for preparing your final project assignment is in this file.

# Below, throughout this file, you should put comments that explain exactly
# what you should do for each step of your project. You should specify
# variable names and processes to use. For example, "Use dictionary
# accumulation with the list you just created to create a dictionary called
# tag_counts, where the keys represent tags on flickr photos and the values
# represent frequency of times those tags occur in the list."

# You can use second person ("You should...") or first person ("I will...") or
# whatever is comfortable for you, as long as you are clear about what should
# be done.

# Some parts of the code should already be filled in when you turn this in: -
# At least 1 function which gets and caches data from 1 of your data sources,
# and an invocation of each of those functions to show that they work  - Tests
# at the end of your file that accord with those instructions (will test that
# you completed those instructions correctly!) - Code that creates a database
# file and tables as your project plan explains, such that your program can be
# run over and over again without error and without duplicate rows in your
# tables. - At least enough code to load data into 1 of your dtabase tables
# (this should accord with your instructions/tests)

######### END INSTRUCTIONS #########

# Put all import statements you need here.
import unittest
import collections
import json
from bs4 import BeautifulSoup
import itertools
import sqlite3
import requests
import sys
import codecs

sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
# Begin filling in instructions....

# First I am going to have to create a cache file and set up a cacheing try and except clause
CACHE_F = "NationalPark.json"
try:
	cache_file = open(CACHE_F, 'r')
	cache_tent = cache_file.read()
	cache_dict = json.loads(cache_tent)
except:
	cache_dict = {}

# Write a function to request data from the National Parks Service state site and save each HTML strings to a list
# 
def get_national_park_data():
	html_data = []
	state_list = ['al','ak','az','ar','ca','co','ct','de','fl','ga','hi','id','il','in','ia','ks','ky','la','me','md','ma','mi','mn','ms','mo','mt','ne','nv','nh','nj','nm','ny','nc','nd','oh','ok','or','pa','ri','sc','sd','tn','tx','ut','vt','va','wa','wv','wi','wy']
	#print(len(state_list))
	for state_abv in state_list:
		if state_abv not in cache_dict:
			baseurl = "https://www.nps.gov/state/" + state_abv + "/index.htm"
			r = requests.get(baseurl)
			html_document = r.text
			#print(type(html_document))
			#soup = BeautifulSoup(html_document, "html.parser") #was used to check and see if html string looked okay
			html_data.append(html_document) #putting all html strings into list html_data after they have been beautified by beautifulsoup
			#print(soup)
			#state_page = soup.find_all("div", {"class": "ContentHeader"}) #used to check if it got info from each state
			#print(state_page.text)
			cache_dict[state_abv] = html_document
			f = open(CACHE_F, 'w')
			f.write(json.dumps(cache_dict))
			f.close()
		else:
			state_info = cache_dict[state_abv]
			#print(type(state_info))
			html_data.append(state_info)
	return html_data

national_parks_data = get_national_park_data() # with no if statement, I am getting output of all 53 html strings, but when I add it, I am only getting one sites html string and am confused as to why
#print(type(national_parks_data))
#json file has output of all 53 sites 
#print(national_parks_data)
#print(cache_dict["co"]) # used to put into simple html reader online


# 
# create National Parks Database with two different tables, Parks, States, and Articles 
# Parks table with:
# 	-Park name as Primary Key (containing a string of the park name)
# 	-State name from the State table (containing a string of the state name)
# 	-Description of the park (containing a string from the description of the park)
# 	-Sites and monuments (containing a string of the parks sites and monuments)
# States table with:
# 	-State name (containing a string of the state name)
# 	-Number of parks in the state (containing an integer of the number of parks)
# 	-Number of vistors of the park annually (containing an integer of the number of vistors)
# 	-Avgerage Temperature in Fahrenheit (containing an integer of avgerage temp)
# Articles table with:
# 	-Article title (containing a string of the article title)
# 	-Parks mentioned in the article (containing strings of the parks mentioned in the article)


conn = sqlite3.connect('NationalParks.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Parks')

table_spec = 'CREATE TABLE IF NOT EXISTS '
table_spec += 'Parks (park_name TEXT PRIMARY KEY, '
table_spec += 'description TEXT, type_of_park TEXT, park_location TEXT, state_name TEXT NOT NULL, FOREIGN KEY (state_name) REFERENCES States(state_name) ON UPDATE SET NULL)'
cur.execute(table_spec)


cur.execute('DROP TABLE IF EXISTS States')

table_spec1 = 'CREATE TABLE IF NOT EXISTS '
table_spec1 += 'States (state_name TEXT PRIMARY KEY, '
table_spec1 += 'park_count INTEGER, park_visitors INTEGER, avg_temp INTEGER)'
cur.execute(table_spec1)


cur.execute('DROP TABLE IF EXISTS Articles')

table_spec2 = 'CREATE TABLE IF NOT EXISTS '
table_spec2 += 'Articles (Article_title TEXT PRIMARY KEY, '
table_spec2 += 'parks_mentioned TEXT)'
cur.execute(table_spec2)

# now that the database file and the tables have been created, begin to load data into the file
# this can either be in the form of a class definition or just load just into one database file
# 	TIP: make sure to sort through the data, extract the text from the html tags
# 		Use BeautifulSoup to parse through the data 

class NationalPark():
	state_name= []
	park_count = []
	park_visitors = [] 
	park_name = [] # tag h3
	park_location = [] # tag h4
	park_type = [] # tag h2
	park_description = [] # tag p
	def __init__(self, soup):
		self.soup = soup
	def extract_html_data(self):
		self.state = self.soup.find("h1",  {"class": "page-title"})
		self.state_name.append(self.state.string)
		#print(self.state_name)
		self.park_numbers = self.soup.find("ul", {'class':"state_numbers"})
		self.count = self.park_numbers.find_all("strong")
		self.park_count.append(self.count[0].string)
		self.park_visitors.append(self.count[1].string)
		#print(self.park_visitors)
		#print(self.park_count)
		return [self.state_name, self.park_count, self.park_visitors]
	def sort_html_data(self):
		self.park_info = self.soup.find("ul", {"id" : "list_parks"})
		self.park = self.park_info.find_all("h3")
		for elem in self.park:
			self.park_name.append(elem.string)
		self.type = self.park_info.find_all("h2")
		for elem in self.type:
			self.park_type.append(elem.string)
		self.description = self.park_info.find_all("p")
		for elem in self.description:
			self.park_description.append(elem.string)
		self.location = self.park_info.find_all("h4")
		for elem in self.location:
			self.park_location.append(elem.string)
		# print(self.park_type)
		# print(self.park_name)
		# print(self.park_description)
		# print(self.park_location)
		return [self.park_name, self.park_type, self.park_description, self.park_location]
		


def NPS_extraction(national_parks_data):
	state_info_list = []
	for elem in national_parks_data:
		soup = BeautifulSoup(elem, "html.parser")
		NPS = NationalPark(soup)
		nps3 = NPS.extract_html_data()
		state_info_list.append(nps3)
	return state_info_list[0]
a = NPS_extraction(national_parks_data)
# print(a)


def park_info_extraction(national_parks_data):
	park_info_list = []
	for elem in national_parks_data:
		soup = BeautifulSoup(elem, "html.parser")
		NPS2 = NationalPark(soup)
		NPS_2 = NPS2.sort_html_data()
		park_info_list.append(NPS_2)
	return park_info_list[0]
c = park_info_extraction(national_parks_data)
print(c)


#define a function to fetch data of the avg_temps
# base url for https://www.currentresults.com/Weather/US/average-annual-state-temperatures.php
def get_weather_data():	
	unique_id = "weather"
	if unique_id not in cache_dict:
		baseurl = "https://www.currentresults.com/Weather/US/average-annual-state-temperatures.php"
		r = requests.get(baseurl)
		weather_doc = r.text
		cache_dict[unique_id] = weather_doc
		f = open(CACHE_F, 'w')
		f.write(json.dumps(cache_dict))
		f.close()
	else:
		weather_info = cache_dict[unique_id]
		state_w =[]
		temps = []
		soup = BeautifulSoup(weather_info, "html.parser")
		w = soup.find("div", {"class":"clearboth"})
		#print(w)
		w_state = w.find_all("a")
		for elem in w_state:
			state_w.append(elem.string)
		wh = w.find_all("tr")
		del wh[0]
		del wh[17]
		del wh[34]
		for elem in wh:
			t = elem.find_all("td")
			temps.append(t[1].string)
		#print(temps)
		#print(state_w)
		#a.append(temps)
		#print(a)
		keys = state_w
		values = temps
		weather_dict = dict(zip(keys, values))
		#print(weather_dict)
	return weather_dict
national_weather_data = get_weather_data()
print(national_weather_data)



b = [value for (key, value) in sorted(national_weather_data.items())]
#print(b)
a.append(b)
#print(a)
state = a[0]
#print(state)
counts = a[1]
#print(counts)
visitors = a[2]
for elem in visitors:
	if elem[0] == "$":
		pos = visitors.index(elem)
		visitors.remove(elem)
		visitors.insert(pos, "N/A")
#print(visitors)
temp = a[3]
#print(temp)


state_information = zip(state, counts, visitors, temp)
for elem in state_information:
	statement = "INSERT OR IGNORE INTO States VALUES (?,?,?,?)"
	cur.execute(statement, elem)

# park = c[0]
# description = c[1]
# location = c[2]
# typ = c[3]

# load the data from the above sorting to the databases 
# for u in state_info:
# 	statement = 'INSERT OR INGNORE INTO States VALUES (?,?,?,?)'

conn.commit()			

# Put your tests here, with any edits you now need from when you turned them
# in with your project plan.

# class Test1(unittest.TestCase):
# 	def test_cache(self):
# 		file1 = open("NPS_cache.json", 'r').read()
# 		self.assertTrue("wy" in file1, "Testing that the state_abv made into the json cache file")
# 	def test_html_str(self):
# 		html_string = NationalParks.fetch_htm_data()
# 		self.assertEqual(type(html_string), type(""))
# 	def test_database(self):
# 		conn = sqlite3.connect('NationalParks.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT * FROM Parks')
# 		output = cur.fetchall()
# 		self.assertTrue(len(output[1])==4, "Testing that Parks table has 4 colums for park name, state, description, and sites")
# 	def test_national_park_headline(self):
# 		self.assertEqual(type(national_park_headline), type(""), 'Testing that the article title of each atricle found is a string')
# 	def test_query(self):
# 		conn = sqlite3.connect('NationalParks.db')
# 		cur = conn.cursor()
# 		cur.execute('SELECT abbrv FROM STATE')
# 		state_abbrv_list = cur.fetchall()
# 		self.assertEqual(type(state_abbrv_list), type([]), "Testing that the list made in query creating a list of states is a list")
# 	def test_park_diction(self):
# 		self.assertEqual(type(park_diction), type({"park":["state", "monuments"]}), "Testing that the park_diction made using collection is a dictionary")
# 		self.assertEqual(type(park_diction.keys()), type([]), "Testing that the park_diction using the dot keys method returns a list of the park names")
# 	def test_states_diction(self):
# 		self.assertEqual(type(states_diction[0]), type("State abbrv"), "Testing that the first element of the states_diction is a string of the state abbrv")	
# ## Remember to invoke all your tests...
# if __name__ == "__main__":
# 	unittest.main(verbosity=2)


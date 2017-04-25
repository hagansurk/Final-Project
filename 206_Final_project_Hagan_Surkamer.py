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


CACHE_F = "NationalPark.json"
try:
	cache_file = open(CACHE_F, 'r')
	cache_tent = cache_file.read()
	cache_dict = json.loads(cache_tent)
except:
	cache_dict = {}

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


class NationalPark():
	state_name= []
	park_count = []
	park_visitors = [] 
	def __init__(self, html_string):
		self.html_string = html_string
		self.soup = BeautifulSoup(self.html_string, "html.parser")
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
		self.park_info_dict = {}
		self.state_park_names = []
		self.state_park_location = []
		self.state_park_type = []
		self.state_park_description = []
		self.largest = self.soup.find("div", {"class" : "ColumnGrid row"})
		self.states = self.largest.find("h1", {"class" : "page-title"})
		self.keys = self.states.string
		#print(self.keys)
		self.park_info = self.largest.find("ul", {"id" : "list_parks"})
		#print(type(self.park_info))
		self.park = self.park_info.find_all("h3")
		#print(self.park)
		for elem in self.park:
			self.name = elem.string
			self.state_park_names.append(self.name)
		#print(self.state_park_names)
		self.type = self.park_info.find_all("h2")
		for elem in self.type:
			self.typ = elem.string
			self.state_park_type.append(self.typ)
		self.description = self.park_info.find_all("p")
		for elem in self.description:
			self.desc = elem.string
			self.state_park_description.append(self.desc)
		self.location = self.park_info.find_all("h4")
		for elem in self.location:
			self.loc = elem.string
			self.state_park_location.append(self.loc)
		self.park_info_dict[self.keys] = [self.state_park_names, self.state_park_type, self.state_park_description, self.state_park_location]
		# print(self.park_type)
		# print(self.park_name)
		# print(self.park_description)
		# print(self.park_location)
		return self.park_info_dict
		#[self.park_name, self.park_type, self.park_description, self.park_location] #, self.park_state]

park_dict_list = []		
for html_string in national_parks_data:
	NPS = NationalPark(html_string)
	v = NPS.extract_html_data()
	u = NPS.sort_html_data()
	park_dict_list.append(u)
#print(v)
	#print(u)
#print(park_dict_list)

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
#print(national_weather_data)



b = [value for (key, value) in sorted(national_weather_data.items())]
#print(b)
v.append(b)
#print(a)
state = v[0]
#print(state)
counts = v[1]
#print(counts)
visitors = v[2]
for elem in visitors:
	if elem[0] == "$":
		pos = visitors.index(elem)
		visitors.remove(elem)
		visitors.insert(pos, "N/A")
#print(visitors)
temp = v[3]
#print(temp)

state_information = zip(state, counts, visitors, temp)
for elem in state_information:
	#print(elem)
	statement = "INSERT OR IGNORE INTO States VALUES (?,?,?,?)"
	cur.execute(statement, elem)
conn.commit()

for elem in park_dict_list:
	keys = elem.keys()
	keys2 = list(keys)
	for i in keys:
		keys2.append(i)
	key = keys2.pop()
	#print(keys2)
	values = elem[key]
	#print(values)
	park_names = values[0]
	#print(park_names)
	park_type = values[1]
	#print(park_type)
	park_desc = values[2]
	#print(park_desc)
	park_loc = values[3]
	#print(park_loc)
	for el in park_names:
		idx = park_names.index(el)
		#print(idx)
		park_tuples = (park_names[idx], park_desc[idx], park_type[idx], park_loc[idx], key)
		statement = "INSERT OR IGNORE INTO Parks VALUES (?,?,?,?,?)"
		cur.execute(statement, park_tuples)
conn.commit()			



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


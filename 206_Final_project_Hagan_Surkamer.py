import unittest
import collections
import json
import re
from bs4 import BeautifulSoup
import itertools
import sqlite3
import requests
import sys
import codecs
import io
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

CACHE_F = "NationalPark.json"
try:
	cache_file = open(CACHE_F, 'r')
	cache_tent = cache_file.read()
	cache_dict = json.loads(cache_tent)
except:
	cache_dict = {}

html_data = []
def get_national_park_data():
	
	#print(len(state_list))
	state_list = ['al','ak','az','ar','ca','co','ct','de','fl','ga','hi','id','il','in','ia','ks','ky','la','me','md','ma','mi','mn','ms','mo','mt','ne','nv','nh','nj','nm','ny','nc','nd','oh','ok','or','pa','ri','sc','sd','tn','tx','ut','vt','va','wa','wv','wi','wy']

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
			#print(cache_dict.keys())
			f = open(CACHE_F, 'w')
			f.write(json.dumps(cache_dict))
			f.close()
			
		else:
			state_info = cache_dict[state_abv]
			#print(cache_dict.keys())
			#print(type(state_info))
			html_data.append(state_info)
	return html_data


national_parks_data = get_national_park_data() 
#print(type(national_parks_data))
#json file has output of all 53 sites 
#print(national_parks_data)
#print(cache_dict["co"]) # used to put into simple html reader online

def get_NPS_article_data():
	NPS_article_data = []
	url_list = []
	art_html_list = []
	html_data = []
	if "NPS_article_info" not in cache_dict:
		baseurl = "https://home.nps.gov/index.htm"
		r = requests.get(baseurl)
		html_document = r.text
		soup = BeautifulSoup(html_document, "html.parser")
		url_add_on = soup.find_all("div", {"class" : "Component Feature -small"})
		baseurl1 = "https://www.nps.gov"
		html_data.append(html_document)
		NPS_article_data.append(html_document)
		#print(html_document)
		href_list = []
		for elem in url_add_on:
			href_tag = elem.find("a")['href']
			#print(href_tag)
			href_list.append(href_tag)
		#print(href_list)
		for elem in href_list:
			url = baseurl1 + elem
			url_list.append(url)
		#print(url_list)
		for elem in url_list:
			r1 = requests.get(elem)
			art_html = r1.text
			#print(art_html)
		
			#print(html_data)
		NPS_article_data.append(art_html)
		cache_dict["NPS_article_info"] = NPS_article_data
		f = open(CACHE_F, 'w')
		f.write(json.dumps(cache_dict))
		f.close()
		return cache_dict["NPS_article_info"]
	else:
		article_info = cache_dict["NPS_article_info"]
		# NPS_article_data.append(article_info)
	return article_info
article_data = get_NPS_article_data()
# print(article_data)
#print(type(article_data))
# print(len(article_data))
# #print(article_data[0])
# #print(article_data[1])
# print(type(article_data[4]))


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
table_spec2 += 'article_text TEXT)'
cur.execute(table_spec2)


class NationalPark(object):
	state_name= []
	park_count = []
	park_visitors = [] 
	def __init__(self, html_string):
		self.html_string = html_string
		self.soup = BeautifulSoup(self.html_string, "html.parser")
	def extract_html_data(self):
		self.state = self.soup.find("h1",  {"class": "page-title"})
		#print(self.state)
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

class Article(object):
	def __init__(self, html_string):
		self.html_string = html_string
		self.soup = BeautifulSoup(self.html_string, "html.parser")
		self.info = self.soup.find_all("div", {"class":"Component Feature -medium"})
		
		self.info3 = self.soup.find("div", {"class" : "Component text-content-size text-content-style"})
		#print(type(self.info3))
		#print(self.info3)
	def extract_titles(self):
		self.title_list = []
		#self.title_list1 =[]
		try:
			for elem in self.info:
				self.title = elem.find_all("h3", {"class" : "Feature-title carrot-end"})
				for t in self.title:
					self.title_list.append(t.string)
			self.info2 = self.soup.find("div", {"class" : "ColumnGrid row"})
			self.article_title1 = self.info2.find_all("h1")
			#print(self.article_title1)
			for title in self.article_title1:
				self.title_list.append(title.string)
			#print(self.title_list)
		except:
			pass
		return self.title_list
	def extract_text(self):
		self.text_list = []
		try:
			self.text = self.info3.find_all("p")
			#print(self.text)
			for elem in self.text:
				self.text_list.append(elem.text)
			#print(text_list)

		except:
			self.info4 = self.soup.find_all("div", {"class":"Component text-content-size text-content-style ArticleTextGroup clearfix"})
			#print(type(self.info4))
			for elem in self.info4:
				self.text = elem.find_all("p")
				for elem in self.text:
					self.text_list.append(elem.text)
		return self.text_list
	def extract_desc(self):
		self.desc_list = []
		try:
			for page in self.info:
				self.desc = page.find("p")#, {"class" : "Feature-description"})
				#print(self.desc)
				#for d in self.desc:
					# d = self.desc.find_all("p")
					# for de in d:
				self.desc_list.append(self.desc.text)
			#print(self.desc_list)
		except:
			pass
		return self.desc_list


title_list = []
text_list = []
desc_list = []
for html_string in article_data:
	article = Article(html_string)
	h = article.extract_titles()
	title_list.append(h)
	g = article.extract_text()
	text_list.append(g)
	d = article.extract_desc()
	desc_list.append(d)

for elem in text_list:
	if len(elem) == 0:
		elem.append("No text on page")
#print(title_list)
yt = title_list[1]
y = title_list[1][-1]
#print(y)
title_list.remove(yt)
title_list.insert(1,[y])
desc_list1 = desc_list[0]
a = text_list[0]
text_list.remove(a)
text_list.insert(0, desc_list1)

k = title_list[0]
title_list.remove(k)
title1 = [k[0]]
title2 = [k[1]]
title_list.insert(0, title1)
title_list.insert(1, title2)
j = text_list[0]
text_list.remove(j)
text1 = [j[0]]
text2 = [j[1]]
text_list.insert(0, text1)
text_list.insert(1,text2)
# print(desc_list1)
# print(title_list)
# #print(type(title_list))
# print(text_list)
	# print(g)
title_list1 = []
for elem in title_list:
	title_list1.append(elem[0])
#print(title_list1)

# #print(v)
	#print(u)
#print(park_dict_list)

def get_weather_data():	
	unique_id = "weather"
	if unique_id not in cache_dict:
		baseurl = "https://www.currentresults.com/Weather/US/average-annual-state-temperatures.php"
		r = requests.get(baseurl)
		weather_doc = r.text
		state_w =[]
		temps = []
		soup = BeautifulSoup(weather_doc, "html.parser")
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
		cache_dict[unique_id] = weather_dict
		f = open(CACHE_F, 'w')
		f.write(json.dumps(cache_dict))
		f.close()
		return cache_dict[unique_id]
	else:
		weather_dict = cache_dict[unique_id]
		# state_w =[]
		# temps = []
		# soup = BeautifulSoup(weather_info, "html.parser")
		# w = soup.find("div", {"class":"clearboth"})
		# #print(w)
		# w_state = w.find_all("a")
		# for elem in w_state:
		# 	state_w.append(elem.string)
		# wh = w.find_all("tr")
		# del wh[0]
		# del wh[17]
		# del wh[34]
		# for elem in wh:
		# 	t = elem.find_all("td")
		# 	temps.append(t[1].string)
		# #print(temps)
		# #print(state_w)
		# #a.append(temps)
		# #print(a)
		# keys = state_w
		# values = temps
		# weather_dict = dict(zip(keys, values))
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
vt = []
visitors = v[2]
#print(visitors)
for elem in visitors:
	elem = re.sub('[,]','',elem)
	vt.append(elem)
for elem in vt:	
	if elem[0]  == "$":
		pos = vt.index(elem)
		vt.remove(elem)
		vt.insert(pos, "N/A")
#print(vt)
temp = v[3]
#print(temp)

state_information = zip(state, counts, vt, temp)
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

text_str_list = []	
text_stri = " ;"		
title_list_2 = []
for elem in text_list:
	a = text_stri.join(elem)
	text_str_list.append(a)


article_db = zip(title_list1,text_str_list)
for elem in article_db:
	#print(elem)
	statement = "INSERT OR IGNORE INTO Articles VALUES (?,?)"
	cur.execute(statement, elem)
conn.commit()

#Task three: create queries 

q1 = 'SELECT state_name, park_count FROM States WHERE park_count >= 20'
cur.execute(q1)
most_parks = cur.fetchall()
#print(most_parks)

q2 = 'SELECT States.state_name, Parks.park_name, States.park_visitors FROM Parks INNER JOIN States on Parks.state_name = States.state_name WHERE States.park_visitors >= 2000000'
cur.execute(q2)
joined_results = cur.fetchall()
#print(joined_results)

q3 = "SELECT States.state_name, Parks.park_name, Parks.park_location, Parks.description, States.avg_temp FROM Parks INNER JOIN States on Parks.state_name = States.state_name WHERE States.avg_temp >= 63" #use inner join to create a query of parks, desc, type, and location for the top five visited states
cur.execute(q3)
most_visited_parks = cur.fetchall()
#print(len(most_visited_parks))

q4 = "SELECT article_text FROM Articles"
cur.execute(q4)
article_db_info = cur.fetchall()
list_article_data = [x[0] for x in article_db_info]
#print(list_article_data)

q5 = "SELECT state_name, park_visitors FROM States WHERE park_visitors >= 10000000"
cur.execute(q5)
most_visitors = cur.fetchall()
#print(most_visitors)

q6 = "SELECT park_name, park_location FROM Parks"
cur.execute(q6)
park_data = cur.fetchall()
#print(park_data)

q7 = "SELECT Article_title, article_text FROM Articles"
cur.execute(q4)
article_info = cur.fetchall()
#print(article_info)


# now manipulate the data
word_lst = []
for line in list_article_data:
	wrds = line.split()
	for word in wrds:
		word_lst.append(word)
#print(word_lst)

out_put = []
for elem in most_visited_parks:
	most_visited_output = "\n\n\nPark name: {}\nPark Location: {}\nState: {}\nPark Description: {}\nAverage State Temperatrue: {}\n\n\n\n\n".format(elem[1], elem[2], elem[0], elem[3], elem[4])
	out_put.append(most_visited_output)
#len(out_put)	

results_file = "results.txt"

with io.open(results_file, 'w', encoding="utf-8") as r_file:
	r_file.write("Results for most popular parks:\n")
	for elem in out_put:
		r_file.write(elem)
	r_file.close()


class Test1(unittest.TestCase):
	def test_cache(self):
		cache_d = cache_dict
		self.assertTrue("wy" in cache_d.keys(), "Testing that the state_abv made into the json cache file")
	def test_html_str(self):
		html_data = get_national_park_data()
		html_string = html_data[0]
		self.assertEqual(type(html_string), type(""))
		html_data2 = get_NPS_article_data()
		html_string2 = html_data2[0]
		self.assertEqual(type(html_string2), type(""))
	def test_database(self):
		conn = sqlite3.connect('NationalParks.db')
		cur = conn.cursor()
		cur.execute('SELECT * FROM Parks')
		output = cur.fetchall()
		self.assertTrue(len(output[1])==5, "Testing that Parks table has 5 colums for park name, state, description, location, and type")
	def test_national_park_headline(self):
		self.assertEqual(type(article_data[0]), type(""), 'Testing that the article title of each atricle found is a string')
	def test_query(self):
		conn = sqlite3.connect('NationalParks.db')
		cur = conn.cursor()
		cur.execute('SELECT state_name FROM States')
		statename_list = cur.fetchall()
		self.assertEqual(type(statename_list), type([]), "Testing that the list made in query creating a list of states is a list")
	def test_weather_diction(self):
		weather_diction = get_weather_data()
		self.assertEqual(type(weather_diction), type({"State name": "avgerage state temp"}), "Testing that the weather_diction returned in get weather data made using dict zip is a dictionary")
		self.assertEqual(sorted(list(weather_diction.keys())), ['Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico', 'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming']
, "Testing that the weather_dict using the dot keys method returns the same list as the list of states from the National Parks site")
	def test_state_park_amount(self):
		conn = sqlite3.connect('NationalParks.db')
		cur = conn.cursor()
		cur.execute("SELECT state_name, park_count FROM States WHERE park_count >= 20")
		output = cur.fetchall()
		self.assertEqual(len(output), 5, "Testing that the query and databases are loaded correctly so that only 5 states are returned when minimum park limit is set at 20")	

if __name__ == "__main__":
	unittest.main(verbosity=2)


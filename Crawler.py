# -*- coding: utf-8 -*-

import requests
import bs4
from bs4 import BeautifulSoup
import os
import sys


def language_selection():
	main_page = 'https://www.sbs.com.au/radio/yourlanguage_podcasts'
	r = requests.get(url=main_page)
	soup = BeautifulSoup(r.text, 'html.parser')
	language_list = soup.find_all('div', class_="field field-name-field-list-url field-type-link-field field-label-hidden")
	links = {i.a.string.lower(): i.a['href'] for i in language_list}
	unsupported_list = ['assyrian','croatian','hebrew','lao','living black','punjabi','portuguese']
	while True:
		try:
			#l = 'mandarin'
			l = input('Please select your language: ').lower()
			if l in unsupported_list:
				raise KeyError
			choice = links[l]
			break
		except KeyError:
			print('Sorry, the language you entered is currently not supported. Please try another one.')
	if l == 'spanish' or l == 'tigrinya':
		return choice
	r = requests.get(url=choice)
	soup = BeautifulSoup(r.text, 'html.parser')
	for i in soup.find_all('a', class_="language-toggle"):
		if i.string != 'English':
			return 'https://www.sbs.com.au' + i['href']


def find_all_resources(link, max_pages=10):
	resources = []
	pages = max_pages
	current_link = link
	while pages != 0:
		pages -= 1
		r = requests.get(url=current_link)
		soup = BeautifulSoup(r.text, 'html.parser')
		# get all resource links on current page
		for i in soup.find_all('div', class_='audio__player-info'):
			resources.append(i.div.next_sibling.next_sibling.a['href'])
		if pages != 0:
			current_link = 'https://www.sbs.com.au' + soup.find('li', class_='pager-next').a['href']
	return resources


def is_string(x):
	return type(x) is bs4.element.NavigableString


def time_is_shorter_than(time, max_time):
	t1 = time.split()
	# if longer than 1 hour or less than 1 minute, exclude it
	if len(t1) != 4:
		return False
	t2 = max_time.split()
	if int(t1[0]) < int(t2[0]):
		return True
	elif int(t1[0]) == int(t2[0]):
		if int(t1[2]) <= int(t2[2]):
			return True
	return False


def text_is_longer_than(length, min_text):
	return length >= min_text


def filtering(time, length, max_time='8 min 0 sec', min_text=100):
	return time_is_shorter_than(time, max_time) and text_is_longer_than(length, min_text)


def scrapper(link):
	r = requests.get(url=link)
	soup = BeautifulSoup(r.text, 'html.parser')
	t = soup.find('div', class_='ds-1col')
	audio = t.find('source')['src']
	des = t.find('div', itemprop='description', recursive=False)
	text = des.p.string
	para = t.find('div', class_='field-type-text-with-summary', recursive=False)
	# determine if the news contains summary paragraphs
	if type(para) is not type(None):
		s = ''
		for i in para.div.div.find_all('p', recursive=False):
			# not an empty paragraph
			if len(i.contents) is not 0:
				# is the string that contains contents wanted
				if is_string(i.contents[0]):
					s += i.contents[0].string
		text += s
	'''
	# filtering
	audio_length = str(t.find('div', class_='field-name-field-duration').contents[1])
	text_length = len(text)
	if filtering(audio_length, text_length):
		return (audio, text)
	'''
	# current path where the program runs
	path = os.path.split(os.path.realpath(__file__))[0]
	# if used for the first time, create a folder for all resources
	if not os.path.isdir(path + '/resources'):	
		os.makedirs(path + '/resources')
	path += '/resources'
	# create a folder for current language if the folder never exists
	language = link.split('/')[-4]
	if not os.path.isdir(path + '/' + language):
		os.makedirs(path + '/' + language)
	path = path + '/' + language
	# use the name of the news to create audio/text files
	file_name = link.split('/')[-1]
	# return directly if the resource has already existed
	if os.path.isdir(path + '/' + file_name):
		return
	else:
		os.makedirs(path + '/' + file_name)
	path = path + '/' + file_name
	# get text
	with open(path + '/' + f'{file_name}.txt', 'w') as f:
		f.write(text)
	# get audio

		
if __name__ == '__main__':
	'''
	link = language_selection()
	resources = find_all_resources(link)
	index = 0
	for item in resources:
		index += 1
		scrapper(item, index)
	'''
	link = 'https://www.sbs.com.au/yourlanguage/cantonese/zh-hans/audiotrack/xin-zhou-ge-ren-ji-qi-ye-fei-wu-hui-shou-ji-hua'
	scrapper(link)

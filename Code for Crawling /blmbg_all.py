# http://investorplace.com
# We can easily find the time and title in the link.

# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import requests, re, time, traceback, csv
from bs4 import BeautifulSoup

def getsoup(url):
	source_code = requests.get(url)
	content = source_code.content
	soup = BeautifulSoup(content,"html.parser")
	return soup

def findpage(statdate,enddate,time_data):
	sdate = []
	for tm_data in time_data:
		for item in tm_data.find_all('time'):
			datetext = str(item.text).strip() #the text include date and time
			cdate = re.search(r'\d\d\d\d',datetext) #the date on articles you arrived
			if cdate:
				cdate = cdate.group()
			else:
				cdate = time.strftime('%Y',time.localtime(time.time()))

			sdtemp = re.search(statdate,datetext) #the date on starting page 	
			while (len(sdate)==0) & (sdtemp is not None):
				if sdtemp:
					sdate = sdtemp.group()		

			edate = re.search(enddate,datetext) #the date on ending page
			if edate:
				edate = edate.group()		
	return sdate,edate,cdate,datetext

def getlinks(soup):
	links = []
	l_data = soup.find_all('div',{"class": "search-result"})
	for item in l_data:
		i2link = item.find_all('h1')
		linkpat = r'href=".*"'
		extlink = re.search(linkpat,str(i2link)).group()[6:-1]
		domain = 'http://www.bloomberg.com'
		link = domain+'/'+extlink
		links.append(link)
	return links

def franglinks(keywords,statyear,endyear):
	#This functions is use to find the range and return links.
	########----------Find the page ranges----------########
	print time.asctime(), ":     Finding the page ranges"
	statpage = 0
	endpage = 0
	spat = r'\w*.*, %d' %statyear
	epat = r'Sep*.*, %d' %endyear
	statdate = re.compile(spat)
	enddate = re.compile((epat))
	links = []

	for i in range(10000):
		try:
			page = i+1
			url = "http://www.bloomberg.com/search?query=%s&sort=time:desc&page=%d" %(keywords,page)
			soup = getsoup(url)
		except Exception,e:
			print e
			time.sleep(60*10)			
			soup = getsoup(url)	

		# Find pages
		time_data = soup.find_all('div',{"class": "search-result"})
		if time_data:
			dates = findpage(statdate,enddate,time_data)
			sdate = dates[0]
			edate = dates[1]
			cdate = int(dates[2])
			datetext = dates[3]

			#starting page
			if (cdate >= statyear):
				if (sdate is not None) & (statpage==0):
					statpage = page+1
					print sdate
					print 'Starting page = ', statpage-1
					print 'Starting Page within 2015 Got'
			else:
				if (statpage==0):
					statpage = page+1
					print 'Starting page = ', statpage-1
					print 'Starting Page Without 2015 Got'

			#ending page
			if (cdate >= endyear) & (cdate < statyear):
				if (edate is not None) & (endpage==0):
					endpage = page
					print edate
					print 'Ending page = ', endpage
					print "Ending Page Got"
			else:
				if (endpage==0) & (cdate < statyear):
					endpage = page
					print 'Ending page = ', endpage
					print "Ending Page Out of 2014 Got"
			
			if cdate < endyear:
				if (statpage==0): statpag = 1
				if (endpage==0): endpage = 1
			
		else:
			print 'Something wrong with the keywords or your xpath was wrong'
			print 'Keywords:', keywords
			break
		
		# Save links
		if (statpage>=1):
			elinks = getlinks(soup)
			for link in elinks:
				links.append(link)

		if (statpage>=1) & (endpage>=1): break 			

	print time.asctime(), ":     Page ranges is from "+str(statpage)+" to "+str(endpage)	
	print time.asctime(), ":     All links retrived"
	return links
	
	##################

########---------- Crawling(Main Part) ----------########
def blmbg(keywords):
	ii = 0
	links = franglinks(keywords,2015,2014)
	fart = open('blmbgart_all.csv','ab+')
	writer = csv.writer(fart)
	writer.writerow(['Number','keywords','Datetime','Title','Url','Text'])
	print '>>>>>-------Downloading Articles-------<<<<<'
	for link in links:
		try:
			soup = getsoup(link)
		except Exception,e:
			print e
			time.sleep(60*10)
			soup = getsoup(link)
				
		tx_data = soup.find_all('div',{'class':'article-body__content'})
		oneart = []
		for item in tx_data:
			try:
				oneart.append(str(item.text.encode('utf8')))
			except Exception,e:
				oneart = ['Not Available',str(e)]
			# for art in item.findAll('p'):
			# 	try:
			# 		oneart.append(str(art.text.encode('utf8')))
			# 	except Exception,e:
			# 		oneart = ['Not Available',str(e)]

		hpat = re.compile(r'\S*headline')
		tl_data = soup.find_all('h1',{'class': hpat})
		for item in tl_data:
			try:
				title = item.text.encode('utf8').strip()
			except Exception,e:
				title = ['Not Available',str(e)]

		try:
			datetime = re.search(r'\d+-\d+-\d+',link).group()
		except Exception,e:
			datetime = ['Not Available',str(e)]


		ii += 1		
		try:
			alldata = ["%d" %ii, keywords, datetime, title, link, oneart]
			writer.writerow(alldata)
			print keywords
			print title,'\n',datetime,'\n',link
			print 'Retrived Articles %d' %ii
			print '\n\n'	
		except Exception,e:
			print keywords
			print link			
			print 'Error occurs when writing into csv: ',str(e),'\n\n'
			alldata = ["%d" %ii, keywords, '', '', link, '']
			writer.writerow(alldata)
			continue

	fart.close()
	print '\nGet', ii, 'articles\n'
	print time.asctime(), ':     All articles retrived and saved'

toget = ['AAPL', 'Iphone', 'Ipad', 'Apple watch', 'macbook',' mac pro', 'Apple IOS', 'Apple OSX', 'Apple pay', 'Apple TV', 'retina', 'imac', 'facetime', 'Apple siri', 'Imessage', '3D touch', 'icloud', 'Apple', 'Ipod', 'Apple music', 'Apple support', 'Apple store', 'Apple service', 'Ibook', 'apple X service', 'apple Xsan', 'Timothy Donald Cook']
# toget = ['apple','Apple Iphone', 'Ipad', 'Apple watch', 'macbook',' mac pro', 'Apple IOS', 'Apple OSX', 'Apple pay', 'Apple TV', 'retina', 'imac', 'Apple facetime', 'Apple siri', 'Apple Imessage', '3D touch', 'icloud', 'Apple', 'Ipod', 'Apple music', 'Apple support', 'Apple store', 'Apple service', 'Ibook', 'apple X service', 'apple Xsan', 'Timothy Donald Cook']

# link = franglinks('iphone',2015,2014)
# for i in link:
# 	print i
# wired('3D touch')
for word in toget:
	blmbg(word)
	print '**********----------<',word,'> completed----------*****'

#!/usr/bin/env python
#=======================================================================================#
# title           :League Table Scraper							#
# description     :Scrapes the web to write league data into a MySQL database		#
# author          :Shane Brennan							#
# date            :20151215								#
# version         :0.1									#
# usage           :python LeagueTableScraper --help					#
# notes           :Scrapes the web, could be volatile if the URL's change.		#
# python_version  :2.7.3								#
#=======================================================================================#

import sys
import os
import json
import re
import operator
import BeautifulSoup
import urllib2
from collections import OrderedDict
from optparse import OptionParser
import MySQLdb as mdb

class IRLFixtureScraper:

	def __init__(self, configFilename=None):
		# Setup the database connection 
		self.conn = None
		self.cursor = None
		
		hostname = None
		username = None
		password = None
		database = None

		if configFilename is None:
			configFilename = 'conf/database.conf'

		# Statically setting this stuff is bad practice, so 
		# read it from an .ini file instead. 
		if os.path.exists(configFilename):
			regex = re.compile('^(hostname|username|password|database)(\s)*=(\s)*[a-zA-Z0-9]+')
			details = open(configFilename, 'r')
			for line in details:
				if regex.match(line):
					tokens = line.split('=')
					if 'username' in tokens[0].rstrip().lower():
						username = tokens[1].rstrip().lstrip()
					elif 'password' in tokens[0].rstrip().lower():
						password = tokens[1].rstrip().lstrip()
					elif 'hostname' in tokens[0].rstrip().lower():
						hostname = tokens[1].rstrip().lstrip()
					elif 'database' in tokens[0].rstrip().lower():
						database = tokens[1].rstrip().lstrip()
		else:
			print 'Error - Cannot find conf/database.conf in current directory!'
			exit(1)

		# Validate the config inputs
		if username is None or password is None or hostname is None or database is None:
			print 'Error - you need to specify the database config in',configFilename
			exit(1)

		# Get the various URL's for the previous Irish League fixtures
		self.leagueCodes = {}
		self.leagueCodes['2015_IRL0_Fixtures'] = 'http://www.rte.ie/sport/results/soccer/premier-division/19259/'

		try:
			self.conn = mdb.connect(hostname, username, password, database);
			self.cursor = self.conn.cursor()
			for key in self.leagueCodes.keys():
				targetURL = self.leagueCodes[key]
				html = self.getRawHTML(targetURL)
				if html is not None:
					self.parseHTML(html)
				else:
					print "Problem reading URL..."
					exit(1)

		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
    			sys.exit(1)

	def insertData(self, fixture):
		""" Inserts the fixture data into the fixture and scorers tables in the 
		    database. This will allow the league table to be generated then via 
		    SQL rather than statically. 
		"""
		try:
			sql = "INSERT INTO 2015_IRL0_Fixtures (LeagueCode, SeasonCode, "
			sql = sql + "Date, HomeTeam, AwayTeam, HomeFT, AwayFT) VALUES "
			sql = sql + '(\'{0}\',\'{1}\',\'{2}\',\'{3}\',\'{4}\',{5},{6});'.format('IRL0',\
				'2015', fixture['Date'], fixture['HomeTeam'],fixture['AwayTeam'], \
				fixture['HomeFT'], fixture['AwayFT'])
			self.cursor.execute(sql)
			print "INSERTING ",fixture['HomeTeam'],"vs",fixture['AwayTeam']			
			self.cursor.execute('COMMIT;')
		except:
			print "Error INSERTING ",fixture['HomeTeam'],"vs",fixture['AwayTeam']

    
	def getRawHTML(self, url):
		""" Returns the raw html from a specified URL or None
		    if there's a problem with the URL.
		"""
		try:
			opener = urllib2.build_opener(RedirectHandler())
			html = opener.open(url).read()
			return html
		except urllib2.HTTPError as e:
			print e.code
			print e.read() 
			return None

	def parseHTML(self, html):
		soup = BeautifulSoup.BeautifulSoup(html)
		resultRows = soup.findAll("tr", "page-")
	
		for row in resultRows:
			tdList = row.findAll("td")

			fixture = {}
			fixture['Date'] = self.formatDate(tdList[0].getText())
			homeGoals = []
			homeScorersList = tdList[1].findAll("li")
			for homeScorer in homeScorersList:
				homeGoals.append(self.getScorer(homeScorer.getText()) )

			fixture['HomeGoals'] = homeGoals
			fixture['HomeTeam'] = self.getTeamName(str(tdList[1]))

			resultRaw = row.findAll("td","results-text-center")[0].getText() 
			resultRaw = resultRaw.replace('&nbsp;-&nbsp;',',')
			results = resultRaw.split(',')
			fixture['HomeFT'] = int(results[0])
			fixture['AwayFT'] = int(results[1])
			fixture['AwayTeam'] = self.getTeamName(str(tdList[3]))

			awayGoals = []
			awayScorersList = tdList[3].findAll("li")
			for awayScorer in awayScorersList:
				awayGoals.append(self.getScorer(awayScorer.getText()))
			fixture['AwayGoals'] = awayGoals

			## IF YOU WANT TO PRINT THE OUTPUT AS JSON, UNCOMMENT BELOW
			# print json.dumps(fixture, sort_keys=True)
			self.insertData(fixture)


			
	def getTeamName(self, html):
		""" Returns the team name between a HTML snippet, i.e., between the td and ul tags, 
		    if a ul tag exists. Also strips out some unicode for apostrophes. 
		"""
		startIndex = html.find('>')
		endIndex = html.find('<ul')

		if startIndex == -1:
			return "NULL"
		else:
			if endIndex != -1:
				return html[startIndex+1:endIndex].replace('\n','').replace('&#39;','\'\'')
			else:
				return html[startIndex+1:].replace('\n','').replace('&#39;','\'\'')

	def getScorer(self, goalText):
		""" The goalText is a string in the form "Joe Bloggs  14'", this 
		    function will split the string by white-space adding non
		    numeric tokens as a player name, and the numerics as the minutes
		"""

		regex = re.compile('^[0-9]+\'')
		tokens = goalText.replace('\n','').rstrip().split(' ')
		name = ""
		min = ""
		for token in tokens:
			if regex.match(token):
				min = int(token.replace('\'',''))
			else:
				if len(name) > 1:
					name = name + " " + str(token)
				else:
					name = name + str(token)

		result = {}
		result['Scorer'] = name.rstrip().replace('\n','').replace('&#39;','\'\'')
		result['Minute'] = min
		return result
		

	def getIndex(self, tag, html):
		try:
			return  html.index(tag)
		except:
			return -1			


	def uescape(self, text):
		return text.encode('utf-8')

	def formatDate(self, dateString):
		""" Converts date string in the format 6 Mar 2015 7:45pm to 2015-03-06.
		"""
		tokens = dateString.split(' ')
		months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
		monthInts = ['01','02','03','04','05','06','07','08','09','10','11','12']

		day = tokens[0]
		if len(day) == 1:
			day = "0"+day

		if tokens[1] in months:
			monthIndex = months.index(tokens[1])
			month = monthInts[monthIndex]
		else:
			print "Cannot parse month",tokens[1]
			exit(1)
		year = tokens[2]

		return (year + '-' + month + '-' + day)


	def convertDateToYYYYMMDD(self, dateString):
		""" Converts a date string of the form 10th May 2015 to 20150510
		"""
		dateTokens = dateString.split(' ')[7:]		
		day = dateTokens[0]
		day = day[:-2]
		if int(day) < 10:
			day = "0"+day
		
		monthTextList = ['January','February','March','April','May','June','July','August','September','October','November','December']
		monthDateList = ['01','02','03','04','05','06','07','08','09','10','11','12']
		month = monthDateList[monthTextList.index(dateTokens[1])]
		
		year = dateTokens[2]
		if len(year) == 2:
			year = "20"+year
			
		return int(year+month+day)
		
class RedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
        	result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        	result.status = code
        	return result
    
	http_error_301 = http_error_303 = http_error_307 = http_error_302


def main(argv):
	parser = OptionParser(usage="Usage: IRLFixtureScraper [CONFIG]")

        parser.add_option("-c", "--config",
                action='store',
                dest='config',
                default=None,
                help='database config details')

	(options, filename) = parser.parse_args()

	scraper = IRLFixtureScraper(options.config)
		
if __name__ == "__main__":
    sys.exit(main(sys.argv))

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

class LeagueTableScraper:

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

		# Get all the league codes and URLs for each league 
		self.leagueCodes = {}
		self.leagueCodes['2015_IRL0_Fixtures'] = 'http://inform.fai.ie/Statsportal/PrintSchedule.aspx?CompID=14'

		try:
			self.conn = mdb.connect(hostname, username, password, database);
			self.cursor = self.conn.cursor()
			for leagueCode in self.leagueCodes.keys():
				fixtureData = self.getFixturesData(self.leagueCodes[leagueCode])
				for dict in getFixtureData:			
		    			cur.execute(sql)
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
    			sys.exit(1)
    

	def getFixturesData(self, fixturesURL):
		leagueTable = None

		try:
			html = self.getRawHTML(fixturesURL)
			if html is not None:
				fixturesData = self.parseFixturesHTML(html)
				print fixturesData
				exit(1)
	
		except KeyError as error:
			print "\nError - Invalid league code (",leagueCode,")..."
			exit(1)

		return leagueTable

	def getRawHTML(self, url):
		""" Returns the raw html from a specified URL or None
		    if there's a problem with the URL.
		"""
		try:
			opener = urllib2.build_opener(RedirectHandler())
			webpage = opener.open(url)
			Soup = BeautifulSoup.BeautifulSoup()
			html=Soup(webpage)
			return html
		except urllib2.HTTPError as e:
			print e.code
			print e.read() 
			return None

	def uescape(self, text):
		return text.encode('utf-8')

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
		
	def parseFixturesHTML(self, html):
		table = []

		if len(html) < 10:
			print "Error - Problems with HTML input to generate league tables..."
			exit(1)

		soup = BeautifulSoup.BeautifulSoup(html)
		teamList = soup.findAll("tr", "team")

		for team in teamList:
			position = team.findAll("span", "position-number")[0].getText()		
			teamName = team.findAll("td", "team-name")[0].getText()
			played = team.findAll("td", "played")[0].getText()

			won = team.findAll("td", "won")[0].getText()
			drawn = team.findAll("td", "drawn")[0].getText()
			lost = team.findAll("td", "lost")[0].getText()

			gf = team.findAll("td", "for")[0].getText()
			ga = team.findAll("td", "against")[0].getText()
			goalDiff = team.findAll("td", "goal-difference")[0].getText()
					
			points = team.findAll("td", "points")[0].getText()
			tablerow = {}
			tablerow['Position'] = position
			tablerow['TeamName'] = teamName
			tablerow['Played'] = played
			tablerow['Won'] = won
			tablerow['Drawn'] = drawn
			tablerow['Lost'] = lost
			tablerow['GoalsFor'] = gf
			tablerow['GoalsAgainst'] = ga
			tablerow['GoalDiff'] = goalDiff
			tablerow['Points'] = points
			table.append(tablerow)

		return table

class RedirectHandler(urllib2.HTTPRedirectHandler):
	def http_error_302(self, req, fp, code, msg, headers):
        	result = urllib2.HTTPError(req.get_full_url(), code, msg, headers, fp)
        	result.status = code
        	return result
    
	http_error_301 = http_error_303 = http_error_307 = http_error_302


def main(argv):
	parser = OptionParser(usage="Usage: LeagueTableScraper [CONFIG]")

        parser.add_option("-c", "--config",
                action='store',
                dest='config',
                default=None,
                help='database config details')

	(options, filename) = parser.parse_args()

	scraper = LeagueTableScraper(options.config)
		
if __name__ == "__main__":
    sys.exit(main(sys.argv))

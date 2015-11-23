#!/usr/bin/env python
#=======================================================================================#
# title           :League Table Scraper							#
# description     :Scrapes the web to write league data into a MySQL database		#
# author          :Shane Brennan							#
# date            :20151123								#
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
import BeautifulSoup as bts
import urllib2
from collections import OrderedDict
from optparse import OptionParser
#import MySQLdb as mdb

class LeagueTableScraper:

	def __init__(self, configFilename=None):

		# Setup the database connection 
		conn = None
		cursor = None
		
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
						username = tokens[1].rstrip()
					elif 'password' in tokens[0].rstrip().lower():
						password = tokens[1].rstrip()
					elif 'hostname' in tokens[0].rstrip().lower():
						hostname = tokens[1].rstrip()
					elif 'database' in tokens[0].rstrip().lower():
						database = tokens[1].rstrip()
		else:
			print 'Error - Cannot find conf/database.conf in current directory!'
			exit(1)

		# Validate the config inputs
		if username is None or password is None or hostname is None or database is None:
			print 'Error - you need to specify the database config in',configFilename
			exit(1)

		# Get all the league codes and URLs for each league 
		self.leagueCodes = {}
		self.leagueCodes['E0']  = 'competition-118996114'
		self.leagueCodes['E1']  = 'competition-118996115'
		self.leagueCodes['E2']  = 'competition-118996116'
		self.leagueCodes['E3']  = 'competition-118996117'
		self.leagueCodes['E4']  = 'competition-118996118'
		self.leagueCodes['E5']  = 'competition-118996307'
		self.leagueCodes['E6']  = 'competition-118996308'
		self.leagueCodes['SC0'] = 'competition-118996176'
		self.leagueCodes['SC1'] = 'competition-118996177'
		self.leagueCodes['SC2'] = 'competition-118996178'
		self.leagueCodes['SC3'] = 'competition-118996179'
		self.leagueCodes['SC4'] = 'competition-118999031'
		self.leagueCodes['SC5'] = 'competition-119003997'
		self.leagueCodes['W1']  = 'competition-118996207'
		self.leagueCodes['NI1'] = 'competition-118996238'
		self.leagueCodes['IE1'] = 'competition-118996240'
		self.leagueCodes['AR1'] = 'competition-999999994'
		self.leagueCodes['AU1'] = 'competition-999999995'
		self.leagueCodes['AT1'] = 'competition-119000919'
		self.leagueCodes['B1']  = 'competition-119000924'
		self.leagueCodes['BR1'] = 'competition-999999996'
		self.leagueCodes['DK1'] = 'competition-119000950'
		self.leagueCodes['N1']  = 'competition-119001012'
		self.leagueCodes['FI1'] = 'competition-119000955'
		self.leagueCodes['F1']  = 'competition-119000981'
		self.leagueCodes['D1']  = 'competition-119000986'
		self.leagueCodes['G1']  = 'competition-119001136'
		self.leagueCodes['I1']  = 'competition-119001017'
		self.leagueCodes['NO1'] = 'competition-119001043'
		self.leagueCodes['PT1'] = 'competition-119001048'
		self.leagueCodes['RU1'] = 'competition-999999990'
		self.leagueCodes['SP1'] = 'competition-119001074'
		self.leagueCodes['SE1'] = 'competition-119001079'
		self.leagueCodes['CH1'] = 'competition-119001105'
		self.leagueCodes['T1']  = 'competition-119001110'
		self.leagueCodes['US1'] = 'competition-999999988'

		try:
			conn = mdb.connect(hostname, username, password, database);
			cursor = con.cursor()
			for key in self.leagueCodes.keys():
				leagueList = self.getLeagueCode(key)
				for dict in leagueList:
					position = dict['Position']
					team = dict['Team']
					played = dict['Played']
					won = dict['Won']
					drawn = dict['Drawn']
					lost = dict['Lost']
					gf = dict['GoalsFor']
					ga = dict['GoalsAgainst']
					gd = dict['GoalDiff']
					pts = dict['Points']
			
					sql = 'INSERT INTO '+key+'_1615 (Position, TeamName, Won, Drawn '
					sql += 'Lost, GoalsFor, GoalsAgainst, GoalDiff, Points) VALUES '
					sql += '({0},\'{1}\',{2},{3},{4},{5},{6},{7},{8});'.format(position, team, \
					        won, drawn, lost, gf, ga, gd, pts)
		    			cur.execute(sql)
		except mdb.Error, e:
			print "Error %d: %s" % (e.args[0],e.args[1])
    			sys.exit(1)
    

	def getLeagueCode(self, leagueCode):
		leagueTable = None

		try:
			tablesBaseURL = 'http://www.bbc.com/sport/football/tables?filter='
			tablesUrl = fixturesBaseURL+self.leagueCodes[leagueCode]+".html"
			tablesHtml = self.getRawHTML(tablesUrl)

			if tablesHtml is not None:
				leagueTable = self.scrapeTables(tablesHtml)
	
		except KeyError as error:
			print "\nError - Invalid league code (",leagueCode,")..."
			exit(1)

		return leagueTable

	def getRawHTML(self, url):
		""" Returns the raw html from a specified URL or None
		    if there's a problem with the URL.
		"""

		try:
			response = urllib2.urlopen(url)
			html = response.read()
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
		
	def scrapeTables(self, html):
		table = []

		if len(html) < 10:
			print "Error - Problems with HTML input to generate league tables..."
			exit(1)

		soup = bts.BeautifulSoup(html)
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

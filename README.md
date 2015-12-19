# IRLFixtureScraper
This script is used to scrape the web for historic Irish League fixtures updating a MySQL database with the 
fixture data. This code requires the BeautifulSoup python library as well as the standard MySQL libraries. 
For the purposes of testing this code is provisioned with a sample MySQL database called mydatabase and a 
series of tables representing the various fixtures and tables scraped.

To install and run this code, ideally on Ubuntu 14.04, you need to install or have, 

- sudo apt-get install python-pip
- sudo apt-get install git 
- sudo pip install BeautifulSoup

The example database is found in the conf directory and can be setup with the commands in the sql/ folder. 

## Setup 

Install a MySQL database on the local test environment if there's not already one there

- sudo apt-get install mysql-server
- sudo apt-get install mysql-client
- sudo apt-get install python-mysqldb

Setup a database, noting the name, and add a new user/password, all this setup SQL is detailed in 
the sql folder. 

## Running the Scraper

python IRLFixtureScraper

or, if you want to speficy the database

python IRLFixtureScraper conf/database.conf

I'm writing this code half-cut after a few bottles of wine, so quality may suffer a bit. What the hell though.

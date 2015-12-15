# LeagueTableScraper
Scrapes League tables and updates a MySQL database with the data. This code requires the BeautifulSoup python
library as well as the standard MySQL libraries. For the purposes of testing this code is provisioned with a 
sample MySQL database called league and a series of tables representing the various leagues scraped. 

To install and run this code, ideally on Ubuntu 14.04, you need to install or have, 

sudo apt-get install python-pip
sudo apt-get install git
sudo apt-get install python-mysqldb

The example database is found in the conf directory and can be setup with the commands in the sql/ folder. 

## Setup 

Install a MySQL database on the local test environment if there's not already one there

sudo apt-get install mysql-server
sudo apt-get install mysql-client

Setup a database, noting the name, and add a new user/password, all this setup SQL is detailed in 
the sql folder. 



## Running the Scraper

python LeagueTableScraper conf/database.conf

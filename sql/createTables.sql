--- Create the user and database, be sure to change details as required
create user 'username'@'localhost' IDENTIFIED BY 'password';
create database mydatabase
GRANT ALL PRIVILEGES ON * . * TO 'username'@'localhost';

--- Now create the fixture tables
create table 2015_IRL0_Fixtures (FixtureSID INT AUTO_INCREMENT, LeagueCode VARCHAR(6) NOT NULL, SeasonCode INT NOT NULL, Date DATE, HomeTeam VARCHAR(64) NOT NULL,  AwayTeam VARCHAR(64) NOT NULL, HomeFT INT NOT NULL, AwayFT INT NOT NULL, HomeHT INT, AwayHT INT, Venue VARCHAR(64), PRIMARY KEY(FixtureSID, LeagueCode , SeasonCode));

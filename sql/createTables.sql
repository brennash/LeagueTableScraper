--- Create the user and database, be sure to change details as required
create user 'username'@'localhost' IDENTIFIED BY 'password';
create database mydatabase
GRANT ALL PRIVILEGES ON * . * TO 'username'@'localhost';

--- Now create the fixture tables
create table 2015_IRL0_Fixtures (FixtureSID INT AUTO_INCREMENT, LeagueCode VARCHAR(6) NOT NULL, SeasonCode INT NOT NULL, Date DATE, HomeTeam VARCHAR(64) NOT NULL,  AwayTeam VARCHAR(64) NOT NULL, HomeFT INT NOT NULL, AwayFT INT NOT NULL, HomeHT INT, AwayHT INT, Venue VARCHAR(64), PRIMARY KEY(FixtureSID, LeagueCode , SeasonCode));

--- Now the league table
create table 2015_IRL0_Table (
  TableSID INT NOT NULL AUTO_INCREMENT, 
  LeagueCode VARCHAR(6), 
  SeasonCode INT, 
  TeamName VARCHAR(64), 
  Win INT, 
  Draw INT, 
  Loss INT, 
  GoalsFor INT, 
  GoalsAgainst INT, 
  GoalDiff INT, 
  Points INT, 
  HomeWin INT, 
  HomeDraw INT, 
  HomeLoss INT, 
  HomeGoalsFor INT, 
  HomeGoalsAgainst INT, 
  HomeGoalDiff INT,
  HomePoints INT, 
  AwayWin INT, 
  AwayDraw INT, 
  AwayLoss INT, 
  AwayGoalsFor INT, 
  AwayGoalsAgainst INT,
  AwayGoalDiff INT, 
  AwayPoints INT, 
PRIMARY KEY(TableSID, LeagueCode, SeasonCode));

--- Get all the distinct teams into a temporary table
CREATE TEMPORARY TABLE IF NOT EXISTS TempTeams AS (SELECT DISTINCT(HomeTeam) FROM 2015_IRL0_Fixtures);


--- Create the procedure to populate the league table
DROP PROCEDURE IF EXISTS UpdateLeagueTable;
DELIMITER ;;
CREATE PROCEDURE UpdateLeagueTable()
BEGIN
DECLARE n INT DEFAULT 0;
DECLARE i INT DEFAULT 0;

DECLARE hwin INT DEFAULT 0;
DECLARE hdraw INT DEFAULT 0;
DECLARE hloss INT DEFAULT 0;
DECLARE hgf INT DEFAULT 0;
DECLARE hga INT DEFAULT 0;

DECLARE awin INT DEFAULT 0;
DECLARE adraw INT DEFAULT 0;
DECLARE aloss INT DEFAULT 0;
DECLARE agf INT DEFAULT 0;
DECLARE aga INT DEFAULT 0;

DECLARE name VARCHAR(64) DEFAULT NULL;
SELECT COUNT(*) FROM TempTeams INTO n;
SET i=0;
WHILE i < n DO
	SELECT HomeTeam FROM TempTeams LIMIT i,1 INTO name;

	-- Get the home details
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT>awayFT INTO hwin;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT=awayFT INTO hdraw;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT<awayFT INTO hloss;
	SELECT SUM(homeFT) FROM 2015_IRL0_Fixtures WHERE homeTeam=name INTO hgf;
	SELECT SUM(awayFT) FROM 2015_IRL0_Fixtures WHERE homeTeam=name INTO hga;

	-- Now get the away details
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT<awayFT INTO awin;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT=awayFT INTO adraw;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT>awayFT INTO aloss;
	SELECT SUM(awayFT) FROM 2015_IRL0_Fixtures WHERE awayTeam=name INTO agf;
	SELECT SUM(homeFT) FROM 2015_IRL0_Fixtures WHERE awayTeam=name INTO aga;


	INSERT INTO 2015_IRL0_Table 
	  (LeagueCode, SeasonCode, TeamName, 
		--- Win,     Draw,     Loss,     GoalsFor,     GoalsAgainst,     GoalDiff,     Points, 
		HomeWin, HomeDraw, HomeLoss, HomeGoalsFor, HomeGoalsAgainst, HomeGoalDiff, HomePoints,
		AwayWin, AwayDraw, AwayLoss, AwayGoalsFor, AwayGoalsAgainst, AwayGoalDiff, AwayPoints) 
	VALUES 
	  ('IRL0', 2015, name, 
		--- (hwin+awin), (hdraw+adraw), (hloss+aloss), (hgf+agf), (hga+aga), (hgf-hga+agf-aga), ((hwin+awin)*3)+(hdraw+adraw),
		hwin, hdraw, hloss, hgf, hga, (hgf-hga), (hwin*3+hdraw),
		awin, adraw, aloss, agf, aga, (agf-aga), (awin*3+adraw));
	SET i = i + 1;
END WHILE;
End;
;;
DELIMITER ;

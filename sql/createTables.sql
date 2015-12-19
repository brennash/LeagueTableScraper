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
  LeaguePosition INT, 
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
  WinPosition TINYINT(1),
  QualPosition TINYINT(1),
  PlayoffPosition TINYINT(1),
  RelegationPosition TINYINT(1),
  MovedUp TINYINT(1),
  MovedDown TINYINT(1),
  StayedSame TINYINT(1),
  Comment VARCHAR(128),
PRIMARY KEY(TableSID, LeagueCode, SeasonCode));


--- Populate the league table
DROP PROCEDURE IF EXISTS UpdateLeagueTable;
DELIMITER ;;
CREATE PROCEDURE UpdateLeagueTable()
BEGIN
DECLARE n INT DEFAULT 0;
DECLARE i INT DEFAULT 0;

DECLARE h_win INT DEFAULT 0;
DECLARE h_draw INT DEFAULT 0;
DECLARE h_loss INT DEFAULT 0;
DECLARE h_gf INT DEFAULT 0;
DECLARE h_ga INT DEFAULT 0;

DECLARE a_win INT DEFAULT 0;
DECLARE a_draw INT DEFAULT 0;
DECLARE a_loss INT DEFAULT 0;
DECLARE a_gf INT DEFAULT 0;
DECLARE a_ga INT DEFAULT 0;

DECLARE name VARCHAR(64) DEFAULT NULL;

CREATE TEMPORARY TABLE IF NOT EXISTS TempTeams AS (SELECT DISTINCT(HomeTeam) FROM 2015_IRL0_Fixtures);

SELECT COUNT(*) FROM TempTeams INTO n;

SET i=0;
WHILE i < n DO
	SELECT HomeTeam FROM TempTeams LIMIT i,1 INTO name;

	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT>awayFT INTO h_win;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT=awayFT INTO h_draw;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE homeTeam=name and homeFT<awayFT INTO h_loss;
	SELECT SUM(homeFT) FROM 2015_IRL0_Fixtures WHERE homeTeam=name INTO h_gf;
	SELECT SUM(awayFT) FROM 2015_IRL0_Fixtures WHERE homeTeam=name INTO h_ga;

	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT<awayFT INTO a_win;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT=awayFT INTO a_draw;
	SELECT COUNT(*) FROM 2015_IRL0_Fixtures WHERE awayTeam=name and homeFT>awayFT INTO a_loss;
	SELECT SUM(awayFT) FROM 2015_IRL0_Fixtures WHERE awayTeam=name INTO a_gf;
	SELECT SUM(homeFT) FROM 2015_IRL0_Fixtures WHERE awayTeam=name INTO a_ga;


	INSERT INTO 2015_IRL0_Table 
	  (LeagueCode, SeasonCode, TeamName, 
	  Win, Draw, Loss,
	  GoalsFor, GoalsAgainst, GoalDiff,
	  Points,
	  HomeWin, HomeDraw, HomeLoss,
	  HomeGoalsFor, HomeGoalsAgainst, HomeGoalDiff,
	  HomePoints,
	  AwayWin, AwayDraw, AwayLoss,
	  AwayGoalsFor, AwayGoalsAgainst, AwayGoalDiff,
	  AwayPoints) 
	VALUES 
	  ('IRL0', 2015, name, 
	  (h_win+a_win), (h_draw+a_draw), (h_loss+a_loss),
	  (h_gf+a_gf), (h_ga+a_ga), (h_gf-h_ga+a_gf-a_ga),
	  ((h_win*3)+(a_win*3)+h_draw+a_draw),
	  h_win, h_draw, h_loss,
	  h_gf, h_ga, (h_gf-h_ga),
	  (h_win*3)+h_draw,
	  a_win, a_draw, a_loss,
	  a_gf, a_ga, (a_gf-a_ga),
	  (a_win*3)+a_draw);
	SET i = i + 1;
END WHILE;
End;
;;
DELIMITER ;

-- Now call the function to update the table
CALL UpdateLeagueTable();

create table 2015_IRL0_Teams (TeamSID INT NOT NULL AUTO_INCREMENT, TeamName VARCHAR(64), TeamLogoURL VARCHAR(256), HomeJerseyURL VARCHAR(256), AwayJerseyURL VARCHAR(256), Stadium VARCHAR(64), Manager VARCHAR(64), Honours VARCHAR(512), PRIMARY KEY(TeamSID));

import mysql.connector
from mysql.connector import Error

def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host = "localhost",
            user = "username",
            password = "password",
            database = "nfl_fantasy"
        )
        print("Successfully connected to MySQL Database")
    except Error as err:
        print(f"Error: {err}")
        
    return connection
    


def create_nfl_team_table():
    """
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INT AUTO_INCREMENT PRIMARY KEY,
            team_name VARCHAR(255) NOT NULL,
            team_abbr VARCHAR(10) NOT NULL,
            division VARCHAR(50) NOT NULL
        );
    """


def create_nfl_player_table():
    """
        CREATE TABLE IF NOT EXISTS Players (
            player_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            position VARCHAR(5) NOT NULL,
            team_id INT,
            price DECIMAL(10, 2) DEFAULT 0.00,
            FOREIGN KEY (team_id) REFERENCES Teams(team_id)
        );
    """


def create_nfl_gameweek_table():
    """
        CREATE TABLE IF NOT EXISTS GameWeeks (
            gameweek_id INT AUTO_INCREMENT PRIMARY KEY,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL
        );
    """

def create_nfl_player_stats_table():  
    """
        CREATE TABLE IF NOT EXISTS PlayerStats (
            stat_id INT AUTO_INCREMENT PRIMARY KEY,
            player_id INT,
            gameweek_id INT,
            touchdowns INT DEFAULT 0,
            receptions INT DEFAULT 0,
            interceptions INT DEFAULT 0,
            field_goals INT DEFAULT 0,
            fantasy_points DECIMAL(5, 2) DEFAULT 0.00,
            FOREIGN KEY (player_id) REFERENCES Players(player_id),
            FOREIGN KEY (gameweek_id) REFERENCES GameWeeks(gameweek_id)
        );
    """

def create_fantasy_team_table():
    """
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INT AUTO_INCREMENT PRIMARY KEY,
            manager_id INT
            offense_players_ids JSON,
            defense_players_ids JSON,
            gameweek_id INT,
            FOREIGN KEY (manager_id) REFERENCES FantasyManager(manager_id),
            FOREIGN KEY (gameweek_id) REFERENCES GameWeeks(gameweek_id)
            team_name VARCHAR(255) NOT NULL,
            team_abbr VARCHAR(10) NOT NULL,
            division VARCHAR(50) NOT NULL
        ) 
    """
    
def create_fantasy_player_table():
    """
        CREATE TABLE IF NOT EXISTS Players (
            player_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            position VARCHAR(5) NOT NULL,
            team_id INT,
            role ENUM('offense', 'defense') NOT NULL,
            price DECIMAL(10, 2) DEFAULT 0.0
            FOREIGN KEY (team_id) REFERENCES Teams (team_id)
        ) 
    """


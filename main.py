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
    
def create_teams_table():
    """
        CREATE TABLE IF NOT EXISTS Teams (
            team_id INT AUTO_INCREMENT PRIMARY KEY,
            team_name VARCHAR(255) NOT NULL,
            team_abbr VARCHAR(10) NOT NULL,
            division VARCHAR(50) NOT NULL
        ) 
    """
    
def create_players_table():
    """
        CREATE TABLE IF NOT EXISTS Players (
            player_id INT AUTO_INCREMENT PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            position VARCHAR(5) NOT NULL,
            team_id INT,
            price DECIMAL(10, 2) DEFAULT 0.0
        ) 
    """
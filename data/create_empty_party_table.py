import json
from flask import app
import psycopg2 as pg2
import sys
sys.path.append(".")

if __name__ == '__main__':
    conn = pg2.connect(database="party_finder",user="postgres",password="ideal-entropy-fanfold-synopsis-grazier",host="localhost",port="55432")
    cur = conn.cursor()
    
    cur.execute("DROP TABLE IF EXISTS Party")
    
    create_empty_party_table_sql = """
        CREATE TABLE Party
        (
            partyID              SERIAL PRIMARY KEY,
            name                 VARCHAR(64) NOT NULL,
            playStartDatetime  DATE NOT NULL,
            leaderID            INTEGER NOT NULL,
            joinLink            VARCHAR(512) NOT NULL,
            gameID               INTEGER NOT NULL
        );
    """
    cur.execute(create_empty_party_table_sql)
    conn.commit()
    
    print("Empty party table created")
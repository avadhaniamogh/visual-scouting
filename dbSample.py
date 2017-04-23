# TODO: only for reference; remove this file
import sqlite3

conn = sqlite3.connect('database.sqlite')
cursor = conn.cursor()

player_id = "30572"
query = "SELECT * FROM Player where player_api_id = ?"
cursor.execute(query, (player_id,))

count = 0
for row in cursor:
   print row[2]
   if count > 10:
       break
   count += 1
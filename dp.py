import sqlite3

conn = sqlite3.connect("games.db") # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()



for row in cursor.execute("""SELECT * FROM games"""):
    print(row)

conn.commit()
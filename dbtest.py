import sqlite3         
con = sqlite3.connect("mydb.db")
cursor = con.cursor()
cursor.execute("SELECT * FROM author")
print(cursor.fetchall())

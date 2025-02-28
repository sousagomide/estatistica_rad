import sqlite3

connection = sqlite3.connect('rad_statistic.db')
cursor = connection.cursor()

cursor.execute(f'DELETE FROM rads')
connection.commit()

cursor.execute(f'DELETE FROM servidores')
connection.commit()
import sqlite3

con = sqlite3.connect('company.db')
cur = con.cursor()
cur.execute('CREATE TABLE employee(name, age) ;')
cur.execute("INSERT INTO employee VALUES('Ali', 28);")
values = [('Brad', 54), ('Ross', 34), ('Muhammad', 28), ('Bilal', 44)]
cur.executemany('insert into employee values(?,?)', values)
con.commit()
con.close()
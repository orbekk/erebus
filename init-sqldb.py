import sqlite3

db = 'erebus.db'

conn = sqlite3.connect(db)
c = conn.cursor()

# Create tables
c.execute("""
create table items (id integer primary key autoincrement,
                    icalendar_id varchar(256),
                    soap_id varchar(256))
""")

c.execute("""
create table icalendar_fields (parent_id integer,
                               icalendar_field varchar(256),
                               icalendar_value text,
                               foreign key (parent_id) references items(id))
""")

conn.commit()

# import sqlite3


# con = sqlite3.connect('data/test_two.db')
# cur = con.cursor()


# cur.execute("""
# CREATE TABLE IF NOT EXISTS NYT_Articles (
#     id INTEGER PRIMARY KEY,
#     pub_date TEXT,
#     full_text TEXT,
#     combined_text TEXT,
#     source REAL,
#     web_url TEXT
# )
# """)
# con.commit()
import os
import sqlite3

db_file = os.getenv("SQLITE_FILE")
if db_file is None:
    db_file = 'posts.db'

def search_db(id_list : list ):
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    placeholders = ', '.join(['?'] * len(id_list))
    query = f"SELECT * FROM posts WHERE id IN ({placeholders}) ORDER BY created_date DESC LIMIT 20"
    res = conn.execute(query, id_list).fetchall()
    conn.close()
    dictionarys =[]
    for row in res:
        dictionarys.append(dict(row))

    return dictionarys

def delete_db(id):
    conn = sqlite3.connect(db_file)
    query = "DELETE FROM posts WHERE id = ?"
    res = conn.execute(query, [id]).rowcount
    conn.commit()
    conn.close()
    if res == 0:
        return False
    else:
        return True


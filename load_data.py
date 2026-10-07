import sqlite3
import os
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers

csv_file = os.getenv("CSV_FILE")
db_file = os.getenv("SQLITE_FILE")

password = os.getenv("ELASTIC_PASSWORD")
login = os.getenv("ELASTIC_LOGIN")
host = os.getenv("ELASTICSEARCH_URL")



if password is None or login is None:
    raise EnvironmentError("ELASTIC_LOGIN and ELASTIC_PASSWORD must be set")
if db_file is None:
    db_file = 'posts.db'
if csv_file is None:
    csv_file = 'posts.csv'
if host is None:
    raise EnvironmentError("ELASTICSEARCH_URL must be set")

client = Elasticsearch(hosts=host, basic_auth=[login, password], verify_certs=False)


mapping = {
    "properties": {
        "id": {"type": "integer"},
        "text": {"type": "text", "analyzer": "russian"}
    }
}
if not (client.indices.exists(index="posts")):
    client.indices.create(index="posts", mappings=mapping)
    print("create map")



conn = sqlite3.connect(db_file)

if len(conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()) == 0:

    pd_csv = pd.read_csv(csv_file)
    pd_csv.to_sql("posts", conn, if_exists='replace',index_label = 'id')
    print('db create')

res = conn.execute('select id, text from posts')
posts =[]

for i in res.fetchall():
    posts.append(
        {
            "_index": "posts",
            "_id": i[0],
            "_source": {
                "id": i[0],
                "text": i[1]
            }
        }
    )

helpers.bulk(client, posts)
client.close()
conn.close()






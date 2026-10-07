import elastic_transport
from fastapi import FastAPI, HTTPException
from elasticsearch import Elasticsearch, NotFoundError

from db import search_db, delete_db
import os


password = os.getenv("ELASTIC_PASSWORD")
login = os.getenv("ELASTIC_LOGIN")
host = os.getenv("ELASTICSEARCH_URL")


if password is None or login is None:
    raise EnvironmentError("ELASTIC_LOGIN and ELASTIC_PASSWORD must be set")
if host is None:
    raise EnvironmentError("ELASTICSEARCH_URL must be set")

app = FastAPI()
client = Elasticsearch(hosts=host, basic_auth=[login, password], verify_certs=False)


@app.get("/search")
def search(query: str):
    try:
        res = client.search(index="posts",query = {"match": {"text":query}}, size=10000, source='id')
    except elastic_transport.ConnectionError:
        raise HTTPException(status_code=503, detail="Connection ElasticSearch Error")

    id_list =[]
    for hit in res['hits']['hits']:
        id_list.append(hit['_id'])
    res = search_db(id_list)

    return res

@app.delete("/posts/{doc_id}")
def delete(doc_id :int):
    message = {"message": "Document Deleted"}
    if  not(delete_db(doc_id)):
        message = {"message": "Document Not Found Database"}


    try:
        client.delete(index="posts",id=str(doc_id))
    except NotFoundError:
        pass
    except elastic_transport.ConnectionError:
        raise HTTPException(status_code=503, detail="Connection ElasticSearch Error")
    return message



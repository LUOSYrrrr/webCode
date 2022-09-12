
from itertools import count
from pydoc_data.topics import topics
from py2neo import Graph,Node, Relationship
import pymongo

client = pymongo.MongoClient('localhost', 27017)  # 建立连接，一般默认
db = client["localhost"]
col = db["t3"]

graph = Graph("http://localhost:7474", auth=("neo4j", "0817"))
a=Node('topic',name='技术')
b=Node('topic',name='数据贩卖')
c=Node('topic',name='诈骗洗钱')
d=Node('topic',name='色情')
e=Node('topic',name='博彩')
f=Node('topic',name='刷粉刷量')

query = {}
projection = {"id":True,"frequency":True,"topic":True}
results = col.find(filter=query, projection=projection)
for result in results:
    relation=result['frequency'] 
    k=Node('id',name=result['id'])
    k.update({'frequency':relation})
    label=result['topic'] 
       
    for l in label:
        if l=='技术':
            r=Relationship(k,'topic',a)
            graph.create(r)
        elif l=='数据贩卖':
            r=Relationship(k,'topic',b)
            graph.create(r)
        elif l=='诈骗洗钱':
            r=Relationship(k,'topic',c)
            graph.create(r)
        elif l=='色情':
            r=Relationship(k,'topic',d)
            graph.create(r)
        elif l=='博彩':
            r=Relationship(k,'topic',e)
            graph.create(r)
        elif l=='刷粉刷量':
            r=Relationship(k,'topic',f)
            graph.create(r)



from flask import Flask, render_template, request, jsonify
import json



from itertools import count
from pydoc_data.topics import topics
from py2neo import Graph,Node, Relationship
from pymongo import MongoClient



def flask_server():
    
    app = Flask(__name__,template_folder='templates')  # 创建一个Flask应用
    neo4j_graph = Graph("http://localhost:7474", auth=("neo4j", "0817"))  # 连接数据库
    @app.route("/")  # 创建路由
    def index():
        return render_template("Neo4j.html")

    @app.route("/query", methods=["POST"])
    def query():
        query = {'id':{'$all':['5588986967']}}  #前端传入用户id
        projection = {"id":True,"topic":True}
        results = col.find(filter=query, projection=projection)

        # cql = "match (c:id) where c.name='%s' return c " % '$id'
        cql = "MATCH (n:id) where n.name=5588986967 RETURN n  " 
        b=graph.run(cql).data()

        for q in graph.run(cql).data():
            node_= q['n']  # 返回的是node
            node_id = node_.identity  # 获取node本身的id
            
        a = graph.run("match(n:id)-[r:topic]->(m:topic) WHERE n.name = 5588986967 RETURN m").data()

        for p in a:
            topic_=p['m']
            topic_id=topic_.identity
            # relation_=p['r']
            # relation_id=relation_.identity
            
            res={
                    "nodes": [
                    {"data": {"id": 'node_.identity', "name": "result['id']", "label": 'id'}},
                    {"data": {"id": 'topic_.identity', "name": "result['topic']", "label": 'topic'}}
                    ],
                    "edges":[{"data": {"source": 'node_.identity', "target": 'topic_.identity', "relationship": 'topic'}}]
                }


        
        return jsonify(res)
    
    # @app.route('/query_entity', methods=['POST'])
    # def query_entity():
    #     name_entity = request.values['name_entity']
    #     rel_outgoing, rel_incoming = entity_query(name_entity, neo4j_graph)
    #     res_query = change_list2json([rel_outgoing, rel_incoming])
    #     return jsonify(res_query)

    # @app.route('/query_rel', methods=['POST'])
    # def query_rel():
    #     name_rel = request.values['name_rel']
    #     print(name_rel)
    #     res_query = rel_query(name_rel, neo4j_graph)
    #     res_query = change_list2json(res_query)
    #     return jsonify(res_query)
    
    app.run(debug=False)
    

if __name__ == '__main__':
    flask_server()
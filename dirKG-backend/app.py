import os
from flask import Flask, jsonify, request, render_template
from nebula2.gclient.net import ConnectionPool
from nebula2.Config import Config
from collections import OrderedDict

app = Flask(__name__)

# @app.route("/")
# def root():
#     return render_template('index.html')

@app.route("/api", methods=["POST"])
def api():
    request_data = request.get_json()
    entity = request_data.get("entity", "")
    if entity:
        resp = query_shareholding(entity)
        data = make_graph_response(resp)
    else:
        data = dict()
    return jsonify(data)

def parse_nebula_graphd_endpoint():
    ng_endpoints_str = os.environ.get('NG_ENDPOINTS', '192.168.145.138:9669,').split(",")
    ng_endpoints = []
    for endpoint in ng_endpoints_str:
        if endpoint:
            parts = endpoint.split(":")
            ng_endpoints.append((parts[0], int(parts[1])))
    return ng_endpoints

def query_shareholding(entity):
    query_string = (
        f"USE file_space; "
        f"MATCH p=(v)-[e:relation*1..2]->(v2) "
        f"WHERE id(v) == '{entity}' "
        f"RETURN p LIMIT 200"
    )

    print(f"[DEBUG] nGQL:\n\t { query_string } \n")

    session = connection_pool.get_session('root', 'nebula')
    resp = session.execute(query_string)
    print(f"[DEBUG] resp:\n\t { resp } \n")

    return resp

def make_graph_response(resp) -> dict:
    nodes, relationships = [], []
    node_ids = set()
    
    for row_index in range(resp.row_size()):
        path = resp.row_values(row_index)[0].as_path()
        
        for node in path.nodes():
            node_id = node.get_id().as_string()
            if node_id not in node_ids:
                node_ids.add(node_id)
                node_data = OrderedDict([
                    ("id", node_id),
                    ("tag", node.tags()[0]),
                    ("Name", str(node.properties(node.tags()[0]).get("Name", ""))),
                    ("Parent", str(node.properties(node.tags()[0]).get("Parent", ""))),
                    ("Route", str(node.properties(node.tags()[0]).get("Route", ""))),
                    ("Creation_time", str(node.properties(node.tags()[0]).get("Creation_time", ""))),
                    ("Label", str(node.properties(node.tags()[0]).get("Label", ""))),
                    ("Depth", str(node.properties(node.tags()[0]).get("Depth", ""))),
                    ("Title", str(node.properties(node.tags()[0]).get("Title", ""))),
                    ("Content", str(node.properties(node.tags()[0]).get("Content", ""))),
                    ("Parent_title", str(node.properties(node.tags()[0]).get("Parent_title", "")))
                ])
                nodes.append(node_data)

        for rel in path.relationships():
            rel_data = {
                "source": rel.start_vertex_id().as_string(),
                "target": rel.end_vertex_id().as_string(),
                "relation": str(rel.properties().get("name", ""))
            }
            relationships.append(rel_data)

    return {"relationships": relationships, "nodes": nodes}

ng_config = Config()
ng_config.max_connection_pool_size = int(
    os.environ.get('NG_MAX_CONN_POOL_SIZE', 10))
ng_endpoints = parse_nebula_graphd_endpoint()
connection_pool = ConnectionPool()

if __name__ == "__main__":
    connection_pool.init(ng_endpoints, ng_config)
    print(f"Nebula Graph connected: { ng_endpoints }")
    try:
        app.run(host="0.0.0.0", port=5001)
    finally:
        connection_pool.close()
else:
    connection_pool.init(ng_endpoints, ng_config)


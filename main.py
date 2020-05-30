from flask import Flask, render_template, request, Response, jsonify
from module.subgraph_tool.graph_utils import subgraph_tool
from module.similarity_tool.nearest_neighbors import NearestNeighbors
from module.graph_lib.constants import *

app = Flask(__name__, static_folder='static')

# define routing
@app.route('/')
@app.route('/home')
def main():
    return render_template("home.html")


@app.route('/tool1')
def tool1():
    return render_template("tool1.html")


@app.route('/tool2')
def tool2():
    return render_template("tool2.html")


@app.route('/tool1/search', methods=['GET', 'POST'])
def graph_search():
    starting_node = request.form.get('starting_node', default = None, type = str)
    ending_node = request.form.get('ending_node', default = None, type = str)
    hops = request.form.get('hops', default = 3, type = int)

    results = subgraph_tool(starting_node, ending_node, hops, max_results=500)

    return jsonify(results)


@app.route('/tool2/search', methods=['GET', 'POST'])
def similarity_search():
    data = request.get_json()
    if "targets" not in data:
        return Response("{'message': 'No targets found'}", status=403, mimetype='application/json')

    targets = data["targets"]
    mode = int(data["mode"])
    k = int(data["k"])

    if mode == 0:
        knn = NearestNeighbors(targets, emb_file_path=GRAPH_EMBEDDING_PATH, n_neighbors=k)
    else:
        knn = NearestNeighbors(targets, emb_file_path=GRAPH_EMBEDDING_PATH, n_neighbors=k, aggregate_method="nearest")

    results = knn.get_neighbors()

    return jsonify(results)


if __name__=='__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

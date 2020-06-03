from flask import Flask, render_template, request, Response, jsonify, send_from_directory
from module.subgraph_tool.subgraph import subgraph_tool
from module.similarity_tool.nearest_neighbors import NearestNeighbors
from module.graph_lib.constants import *

app = Flask(__name__, static_folder='static')

# define routing
@app.route('/')
@app.route('/home')
def main():
    return render_template("home.html")

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    mode = request.form.get('mode', default = 0, type = int)

    try:
        results = subgraph_tool(starting_node, ending_node, hops, max_results=500, mode=mode)
    except:
        return Response("{'message': 'the data was malformed in some way'}", status=400, mimetype='application/json')

    return jsonify(results)


@app.route('/tool2/search', methods=['GET', 'POST'])
def similarity_search():
    data = request.get_json()
    if "targets" not in data:
        return Response("{'message': 'No targets found'}", status=400, mimetype='application/json')
    if "mode" not in data:
        return Response("{'message': 'No mode found'}", status=400, mimetype='application/json')
    if "k" not in data:
        return Response("{'message': 'No k found'}", status=400, mimetype='application/json')
    if "concept" not in data:
        return Response("{'message': 'No concept found'}", status=400, mimetype='application/json')

    targets = data["targets"]
    concept = data["concept"]

    try:
        mode = int(data["mode"])
        k = int(data["k"])
    except:
        return Response("{'message': 'k or mode is not an integer'}", status=400, mimetype='application/json')

    try:
        if mode == 0:
            knn = NearestNeighbors(targets, concept=concept, n_neighbors=k)
        else:
            knn = NearestNeighbors(targets, concept=concept, n_neighbors=k, aggregate_method="nearest")
    except:
        return Response("{'message': 'knn failed due to unknown values'}", status=400, mimetype='application/json')

    results = knn.get_neighbors()

    return jsonify(results)


if __name__=='__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)

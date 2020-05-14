import os
from flask import Flask, render_template, request

def create_app(config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_mapping(
                    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite')
                )
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

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

    @app.route('/tool1/search', methods=['POST'])
    def graph_search():
        starting_node = request.form.get('starting_node', default = None, type = str)
        ending_node = request.form.get('ending_node', default = None, type = str)
        hops = request.form.get('hops', default = 3, type = int)
        return {"start" : starting_node, "end": ending_node, "hops": hops}

    return app
import os
from flask import Flask, render_template

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

    return app
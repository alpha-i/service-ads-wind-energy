from flask import Blueprint, g, render_template

data_exploration_blueprint = Blueprint('data_exploration', __name__)


@data_exploration_blueprint.route('/')
def index():
    return render_template('data_exploration/index.html')

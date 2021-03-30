"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User , Todo

#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/todo', methods=['GET'])
def handle_todo():
    todo_all = Todo.query.all()
   
    my_todo= list(map(lambda x:x.serialize(), todo_all))
    return jsonify(my_todo), 200

@app.route('/todo', methods=['POST'])
def add_todo():

    # First we get the payload json
    body = request.get_json()

    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'label' not in body:
        raise APIException('You need to specify the tasks', status_code=400)        

    # at this point, all data has been validated, we can proceed to inster into the bd
    new_Todo = Todo(label=body['label'], is_done=body['done'])
    db.session.add(new_Todo)
    db.session.commit()
    return "ok", 200

@app.route('/todo/<int:id>', methods=['DELETE'])
def remove_todo(id):

    item = Todo.query.get(id)
    if item is None:
        raise APIException('Task not found', status_code=404)

    db.session.delete(item)
    db.session.commit()

    return jsonify("Task deleted successfully."), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

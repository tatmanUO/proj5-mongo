import os
from flask import Flask, redirect, url_for, request, render_template
from pymongo import MongoClient

app = Flask(__name__)

# Step 1: create a client object
# The environment variable DB_PORT_27017_TCP_ADDR is the IP of a linked docker
# container (IP of the database). Generally "DB_PORT_27017_TCP_ADDR" can be set to
# "localhost" or "127.0.0.1".
#
# For windows:
# 1) Run "docker volume prune"
# 2) client = MongoClient('mongodb://mongodb:27017/')
# Now everything should work.
#
client = MongoClient(os.environ['DB_PORT_27017_TCP_ADDR'], 27017)

# Step 2: connect to the DB
db = client.tododb

@app.route('/')
def todo():
    _items = db.tododb.find()
    items = [item for item in _items]

    return render_template('todo.html', items=items)

# https://www.diffen.com/difference/GET-vs-POST-HTTP-Requests
@app.route('/new', methods=['POST'])
def new():
    item_doc = {
        'name': request.form['name'],
        'description': request.form['description']
    }
    db.tododb.insert_one(item_doc)

    return redirect(url_for('todo'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

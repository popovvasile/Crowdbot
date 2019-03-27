from flask import Flask, jsonify
from flask import request

app = Flask(__name__)

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol',
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web',
        'done': False
    }
]


@app.route('/', methods=['GET'])
def get_tasks():
    return jsonify({'tasks': tasks})


@app.route('/', methods=['POST'])
def create_task():

    print(request.form)
    task = {
        'id': tasks[-1]['id'] + 1,
        'title': 'title',
        'description': 'desc',
        'done': False
    }
    tasks.append(task)
    return jsonify({'task': task}), 201


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



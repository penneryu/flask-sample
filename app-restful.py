from flask import Flask, make_response
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
api = Api(app)
auth = HTTPBasicAuth()

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

class TaskListAPI(Resource):
	decorators = [auth.login_required]
	def __init__(self): 
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('title', type = str, required = True, help = 'No task title provided', location = 'json')
		self.reqparse.add_argument('description', type = str, default = "", location = 'json')		
		super(TaskListAPI, self).__init__()

	def get(self):
		return {'tasks': tasks}
	
	def post(self):
		task = {
			'id': tasks[-1]['id'] + 1,
			'done': False
		}
		args = self.reqparse.parse_args()
		for k, v in args.iteritems():
			if v != None: 
				task[k] = v
		tasks.append(task)
		return {'task': task}, 201

class TaskAPI(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('title', type = str, location = 'json')
		self.reqparse.add_argument('description', type = str, location = 'json')
		self.reqparse.add_argument('done', type = bool, location = 'json')
		super(TaskAPI, self).__init__()

	def put(self, id):
		task = filter(lambda t: t['id'] == id, tasks)
		if len(task) == 0:
			abort(404)
		task = task[0]
		args = self.reqparse.parse_args()
		for k, v in args.iteritems():
			if v != None:
				task[k] = v
		return { 'task': task}

api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint = 'tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<int:id>', endpoint = 'task')

@auth.get_password
def get_password(username):
	if username == 'penner':
		return 'python'
	return None


if __name__ == '__main__':
	app.run()


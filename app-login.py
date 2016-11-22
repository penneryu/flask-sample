import os
from flask import Flask, make_response, url_for, abort, g
from flask_restful import Api, Resource, reqparse
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'https://github.com/penneryu'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
api = Api(app)
auth = HTTPBasicAuth()
db = SQLAlchemy(app)

class User(db.Model):
	__tablename__ = 'users'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), index=True)
	password_hash = db.Column(db.String(64))

	def hash_password(self, password):
		self.password_hash = pwd_context.encrypt(password)
	
	def verify_password(self, password):
		return pwd_context.verify(password, self.password_hash)

	def generate_auth_token(self, expiration=600):
		s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
		return s.dumps({'id': self.id})
	
	@staticmethod
	def verify_auth_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			data = s.loads(token)
		except SignatureExpired:
			return None 
		except BadSignature:
			return None
		user = User.query.get(data['id'])
		return user

@auth.verify_password
def verify_password(username_or_token, password):
	user = User.verify_auth_token(username_or_token)
	if not user:
		user = User.query.filter_by(username=username_or_token).first()
		if not user or not user.verify_password(password):
			return False
	g.user = user
	return True

class UserListAPI(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('username', type = str, required = True, help = 'No username provided', location = 'json')
		self.reqparse.add_argument('password', type = str, required = True, help = 'No password provided', location = 'json')
		super(UserListAPI, self).__init__()

	def post(self):
		args = self.reqparse.parse_args()
		username = args['username']
		password = args['password']
		if User.query.filter_by(username = username).first() is not None:
			abort(400)
		user = User(username = username)
		user.hash_password(password)
		db.session.add(user)
		db.session.commit()
		return { 'username': user.username }, 201, {'Location': url_for('user', id = user.id, _external = True)}

class UserAPI(Resource):
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument('id', type = int, required = True, help = 'No id provider')
		super(UserAPI, self).__init__()

	def get(self, id):
		user = User.query.get(id)
		if not user:
			abort(404)
		return {'username': user.username}

class TokenAPI(Resource):
	decorators = [auth.login_required]
	def get(self):
		token = g.user.generate_auth_token(600)
		return {'token': token.decode('ascii'), 'duration': 600}

class ResourceAPI(Resource):
	decorators = [auth.login_required]
	def get(self):
		return {'data': 'Hello, %s!' % g.user.username}

api.add_resource(UserListAPI, '/user/api/v1.0/users', endpoint = 'users')
api.add_resource(UserAPI, '/user/api/v1.0/user/<int:id>', endpoint = 'user')
api.add_resource(TokenAPI, '/user/api/v1.0/token', endpoint = 'token')
api.add_resource(ResourceAPI, '/user/api/v1.0/resource', endpoint = 'resource')


if __name__ == '__main__':
	if not os.path.exists('db.sqlite'):
		db.create_all()
	app.run(debug = True)


# flask-sample

use flask to build simple restfull webservice on python

### base

		pip install flask
		pip install flask-httpauth
		pip install flask-restful

### app-login.py

	use flask_sqlalchemy create sqlite database
	
- create user
		
		curl -i -X POST -H "Content-Type: application/json" -d '{"username":"penner","password":"python"}' http://127.0.0.1:5000/user/api/v1.0/users
		
- get user token

		curl -u penner:python -i -X GET http://127.0.0.1:5000/user/api/v1.0/token
		
		{
    		"duration": 600, 
    		"token": "eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ3OTc5ODIyMywiaWF0IjoxNDc5Nzk3NjIzfQ.eyJpZCI6NH0.siUl8QfAgM7EUnhrVSQRzq8zelF0vpkFW6uwuBemMsM"
		}
		
- use the token get resource from server

		curl -u eyJhbGciOiJIUzI1NiIsImV4cCI6MTQ3OTc5ODIyMywiaWF0IjoxNDc5Nzk3NjIzfQ.eyJpZCI6NH0.siUl8QfAgM7EUnhrVSQRzq8zelF0vpkFW6uwuBemMsM: -i -X GET http://127.0.0.1:5000/user/api/v1.0/resource
		
		{
    		"data": "Hello, penner!"
		}
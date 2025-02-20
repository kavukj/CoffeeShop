from operator import imod
import os
import re
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth, get_token_auth_header, check_permissions, verify_decode_jwt

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
#db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks",methods=["GET"])
def drinks():
    try:      
        drinks = Drink.query.all()
        drink_format = [drink.short() for drink in drinks]
        return jsonify({
            'success':True,
            'drinks':drink_format
        })
    except SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail",methods=["GET"])
@requires_auth("get:drinks")
def drinksDetail(payload):
    try:     
        drinks = Drink.query.all()
        drink_format = [drink.long() for drink in drinks]
        return jsonify({
            'success':True,
            'drinks':drink_format
        })
    except SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks",methods=["POST"])
@requires_auth("post:drinks")
def add_drinks(payload):
    body = request.get_json()
    try:
        title= body['title']
        recipe=body['recipe']
        #Checks if the recipe is an dict or not
        if isinstance(recipe, dict):
            recipe = [recipe]            
        drink = Drink(title=title,recipe=json.dumps(recipe))   
        drink.insert()
        drinks = Drink.query.all()
        drink_format = [drink.long() for drink in drinks]
        return jsonify({
            'success':True,
            'drinks':drink_format
        })
    except SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>",methods=["PATCH"])
@requires_auth("patch:drinks")
def edit_drinks(payload, id):
    body = request.get_json()
    drink = Drink.query.filter(Drink.id == id).one_or_none()         
    if not drink:
        abort(404)
    try:
        recipe=body['recipe'] #Type list
        drink.title=body['title'],
        drink.recipe = json.dumps(recipe) #Type string  
        drink.update()
        drinks = Drink.query.all()
        drink_format = [drink.long() for drink in drinks]
        return jsonify({
            'success':True,
            'drinks':drink_format
        })
    except SQLAlchemyError as e:
        print(e)
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>",methods=["DELETE"])
@requires_auth("delete:drinks")
def delete_drinks(payload, id):
    drink = Drink.query.filter(Drink.id == id).one_or_none()         
    if not drink:
        abort(404)
    try:
        drink.delete()
        drinks = Drink.query.all()
        drink_format = [drink.long() for drink in drinks]
        return jsonify({
            'success':True,
            'delete':id,
            'drinks':drink_format
        })
    except SQLAlchemyError as e:
        print(e)
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "Bad Request"
    }), 400
    
@app.errorhandler(500)
def server_error(error):
   return jsonify({
        "success": False, 
        "error": 500,
        "message": "Internal Server Error"
    }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "Page Not Found"
    }), 404

@app.errorhandler(422)
def unproccesable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "Cannot Process Request"
    }), 422

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": 'Method Not Allowed'
    }), 405

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), error.status_code

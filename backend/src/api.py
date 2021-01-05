import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES

@app.route('/drinks', methods = ['GET'])
def get_drinks():
    try:
        drinks = [d.short() for d in Drink.query.all()]
        return jsonify({
            "sucess": True, 
            "drinks": drinks  
        })
    except Exception:
        abort(500)


@app.route('/drinks-detail', methods = ['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks = [d.long() for d in Drink.query.all()]
        return jsonify({
            "sucess": True, 
            "drinks": drinks
        })
    except Exception:
        abort(500)

@app.route('/drinks', methods = ['POST'])
@requires_auth('post:drinks')
def drinks(payload):
    body = request.get_json()
    print(body)
    try:
        new_drink = Drink(title = body['title'], recipe = json.dumps(body['recipe']))
        new_drink.insert()
        return jsonify({
            "success": True,
            "drinks": new_drink.long()
        })
    except Exception:
        abort(422)

@app.route('/drinks/<int:id>', methods = ['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        if 'title' in body:
            drink.title = body['title']
        if 'recipe' in body:
            drink.recipe = json.dumps(body['recipe'])
        drink.update()
        return jsonify({
            "success": True,
            "drinks": [drink.long()]
        })
    except Exception:
        abort(422)

@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinl(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort(404)
    try:
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
    except Exception:
        abort(500)


## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
            "success": False, 
            "error": 422,
            "message": "unprocessable"
        }), 422

@app.errorhandler(404)
def notfound(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found"
    }), 404

@app.errorhandler(AuthError)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error['description']
    }), 401

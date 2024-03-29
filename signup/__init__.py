import json
import azure.functions as func
import os
import pymongo
import bcrypt

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les données de la requête
        request = req.get_json()
        username = request.get('username')
        email = request.get('email')
        password = request.get('password')

        # Vérifier si toutes les données nécessaires sont présentes
        if not all([username, email, password]):
            return func.HttpResponse(json.dumps({
                "signup": "failed",
                "message": "Please provide a username, an email and a password."
                }), status_code=400, mimetype='application/json')
            
         # Hashage du mot de passe
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # Connection à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        collection = db['users']

        # Vérifier si un utilisateur avec le même email existe déjà
        if collection.find_one({"email": email}):
            return func.HttpResponse(json.dumps({
                "signup": "failed",
                "message": "User with the same email already exists."
                }), status_code=409, mimetype='application/json')

        # Insérer le nouvel utilisateur
        user = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "role": "user"
        }
        collection.insert_one(user)

        return func.HttpResponse(json.dumps({
            "signup": "success",
            "user": {
                "username": username,
                "email": email,
                "role": "user"
            }
            }), status_code=201, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error during the creation of user: {str(e)}", status_code=500)

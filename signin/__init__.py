import json
import azure.functions as func
import os
import pymongo
import bcrypt  

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les données de la requête
        request = req.get_json()
        email = request.get('email')
        password = request.get('password')

        # Vérifiez si l'email et le mot de passe sont fournis
        if not email or not password:
            return func.HttpResponse(json.dumps({
                "signin": "failed",
                "message": "Please provide an email and a password."
                }), status_code=400, mimetype='application/json')
            
        # Encodage du mot de passe en bytes
        password = password.encode('utf-8')

        # Connection à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        collection = db['users']

        # Rechercher un utilisateur par email
        user = collection.find_one({"email": email})

        if user:
            # Vérifier le mot de passe
            if bcrypt.checkpw(password, user['password']):
                return func.HttpResponse(json.dumps({
                    "signin": "success",
                    "user": {
                        "username": user['username'],
                        "email": user['email'],
                        "role": user['role']
                    }
                    }), status_code=200, mimetype='application/json')
            else:
                return func.HttpResponse(json.dumps({
                    "signin": "failed",
                    "message": "Incorrect password."
                    }), status_code=401, mimetype='application/json')
        else:
            return func.HttpResponse(json.dumps({
                "signin": "failed",
                "message": "User with the provided email does not exist."
                }), status_code=404, mimetype='application/json')

    except Exception as e:
        return func.HttpResponse(f"Error during sign-in process: {str(e)}", status_code=500)

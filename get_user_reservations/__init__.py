import json
import azure.functions as func
import os
import pymongo

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer l'email du participant à partir des paramètres de la requête
        participant_email = req.params.get('email')
        
        if not participant_email:
            return func.HttpResponse(json.dumps({
                "message": "Email parameter is missing."
                }), status_code=400)

        # Connexion à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        
        # Accéder à la collection de réservations
        reservations_collection = db['reservations']

        # Trouver toutes les réservations pour le participant donné
        reservations = list(reservations_collection.find({"participant": participant_email}))

        # Transformer les réservations en un format JSON sérialisable
        reservations_data = [{
            "event_name": reservation["event_name"],
            "date": reservation["date"],
            "participant": reservation["participant"]
        } for reservation in reservations]

        # Renvoyer les réservations trouvées
        return func.HttpResponse(json.dumps({
            "reservations": reservations_data
        }), status_code=200, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error retrieving reservations: {str(e)}", status_code=500)

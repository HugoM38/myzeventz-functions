import json
import azure.functions as func
import os
import pymongo
from datetime import datetime, timezone

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les données de la requête
        request = req.get_json()
        event_name = request.get('event_name')
        participant_email = request.get('email')
        
        # Vérifier si toutes les données nécessaires sont présentes
        if not all([event_name, participant_email]):
            return func.HttpResponse(json.dumps({
                "event_reservation": "failed",
                "message": "Please provide all required fields: event_name and email."
                }), status_code=400)

        # Connexion à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        
        # Vérifications
        events_collection = db['events']
        reservations_collection = db['reservations']
        users_collection = db['users']

        event = events_collection.find_one({"name": event_name})
        if not event:
            return func.HttpResponse(json.dumps({
                "event_reservation": "failed",
                "message": "Event not found"
                }), status_code=404)
            
        participant = users_collection.find_one({"email": participant_email})
        if not participant:
            return func.HttpResponse(json.dumps({
                "event_reservation": "failed",
                "message": "Participant not found"
                }), status_code=404)
        
        if reservations_collection.count_documents({"event_name": event_name}) > event['participant_limit']:
            return func.HttpResponse(json.dumps({
                "event_reservation": "failed",
                "message": "Event is full"
                }), status_code=400)

        if reservations_collection.find_one({"event_name": event_name, "participant": participant_email}):
            return func.HttpResponse(json.dumps({
                "event_reservation": "failed",
                "message": "Participant already registered"
                }), status_code=400)

        # Enregistrer la réservation
        timestamp = datetime.now(timezone.utc).timestamp()
        
        reservation = {
            "event_name": event_name,
            "participant": participant_email,
            "date": timestamp
        }
        reservations_collection.insert_one(reservation)

        return func.HttpResponse(json.dumps({
            "event_reservation": "success",
            "reservation": {
                "event_name": event_name,
                "participant": participant_email,
                "date": timestamp
            },
            "message": "Reservation successful"
            }), status_code=201)
    except Exception as e:
        return func.HttpResponse(f"Error during reservation: {str(e)}", status_code=500)

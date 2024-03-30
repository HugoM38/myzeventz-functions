import json
import azure.functions as func
import os
import pymongo

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les données de la requête
        request = req.get_json()
        name = request.get('name')
        description = request.get('description')
        organizer_email = request.get('organizer')
        date = request.get('date')
        event_type = request.get('event_type') 
        location = request.get('location') 
        participant_limit = request.get('participant_limit') 

        # Vérifier si toutes les données nécessaires sont présentes
        if not all([name, description, organizer_email, date, event_type, location, participant_limit]):
            return func.HttpResponse(json.dumps({
                "event_creation": "failed",
                "message": "Please provide all required fields: name, description, organizer, date, event_type, location, and participant_limit."
                }), status_code=400, mimetype='application/json')

        # Connection à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        
        # Vérifier si l'organisateur existe et a le rôle "organizer"
        users_collection = db['users']
        organizer = users_collection.find_one({"email": organizer_email, "role": "organizer"})
        if not organizer:
            return func.HttpResponse(json.dumps({
                "event_creation": "failed",
                "message": "Organizer not found or does not have the organizer role."
                }), status_code=404, mimetype='application/json')
        
        events_collection = db['events']
        # Vérifier si un événement avec le même nom existe déjà
        if events_collection.find_one({"name": name}):
            return func.HttpResponse(json.dumps({
                "event_creation": "failed",
                "message": "An event with the same name already exists."
                }), status_code=409, mimetype='application/json')

        # Insérer le nouvel événement
        
        events_collection.insert_one({
            "name": name,
            "description": description,
            "organizer": organizer_email,
            "date": date,
            "event_type": event_type, 
            "location": location,  
            "participant_limit": participant_limit  
        })

        return func.HttpResponse(json.dumps({
            "event_creation": "success",
            "event": {
                "name": name,
                "description": description,
                "organizer": organizer_email,
                "date": date,
                "event_type": event_type, 
                "location": location,  
                "participant_limit": participant_limit  
            
            }  
            }), status_code=201, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error during the creation of event: {str(e)}", status_code=500)

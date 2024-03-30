import json
import azure.functions as func
import os
import pymongo

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Connection à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        events_collection = db['events']
        
        # Récupérer tous les événements
        events = list(events_collection.find({}, {'_id': False}))

        # Vérifier si des événements ont été trouvés
        if events:
            return func.HttpResponse(body=json.dumps({
                "events": events,
                "message": "Events fetched successfully."
            }), status_code=200, mimetype='application/json')
        else:
            return func.HttpResponse(json.dumps({
                "events": [],
                "message": "No events found."
            }), status_code=404, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error fetching events: {str(e)}", status_code=500)

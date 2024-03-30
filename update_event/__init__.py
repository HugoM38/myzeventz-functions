import json
import azure.functions as func
import os
import pymongo

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer les données de la requête
        request = req.get_json()
        event_name = request.get('name') 
        update_fields = request.get('update_fields') 

        # Vérifier si le nom de l'événement et les champs à mettre à jour sont présents
        if not event_name or not update_fields:
            return func.HttpResponse(json.dumps({
                "update": "failed",
                "message": "Please provide the event name and fields to update."
            }), status_code=400, mimetype='application/json')

        # Exclure explicitement la modification de l'organisateur
        update_fields.pop('organizer', None) 

        # Connection à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        events_collection = db['events']

        # Si le nom est parmi les champs à mettre à jour, vérifier s'il est déjà pris
        new_name = update_fields.get('name')
        if new_name and events_collection.find_one({"name": new_name}):
            return func.HttpResponse(json.dumps({
                "update": "failed",
                "message": f"An event with the name '{new_name}' already exists."
            }), status_code=409, mimetype='application/json')

        # Rechercher l'événement par son nom actuel et mettre à jour les champs spécifiés
        result = events_collection.update_one({"name": event_name}, {"$set": update_fields})

        # Vérifier si un document a été modifié
        if result.matched_count == 0:
            return func.HttpResponse(json.dumps({
                "update": "failed",
                "message": "Event not found."
            }), status_code=404, mimetype='application/json')
        elif result.modified_count == 0:
            return func.HttpResponse(json.dumps({
                "update": "failed",
                "message": "No changes were made to the event."
            }), status_code=304, mimetype='application/json')
        else:
            return func.HttpResponse(json.dumps({
                "update": "success",
                "message": f"Event '{event_name}' updated successfully."
            }), status_code=200, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error updating event: {str(e)}", status_code=500)

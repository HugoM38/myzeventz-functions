import azure.functions as func
import os
import pymongo
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer le nom de l'événement depuis les paramètres de la requête
        name = req.params.get('name')
        
        if not name:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                name = req_body.get('name')

        # Vérifier si le nom de l'événement a été fourni
        if not name:
            return func.HttpResponse(
                json.dumps({
                    "event_deletion": "failed",
                    "message": "Please pass a name on the query string or in the request body"
                    }),
                status_code=400
            )

        # Connection à Cosmos DB (MongoDB)
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        events_collection = db['events']
        
        # Recherche et suppression de l'événement par son nom
        result = events_collection.delete_one({"name": name})
        
        if result.deleted_count == 0:
            # Aucun événement trouvé avec ce nom
            return func.HttpResponse(
                json.dumps({
                    "event_deletion": "failed",
                    "message": "No event found with this name."
                    }),
                status_code=404,
                mimetype="application/json"
            )
        else:
            # Événement supprimé avec succès
            return func.HttpResponse(
                json.dumps({
                    "event_deletion": "success",
                    "message": "Event successfully deleted."
                    }),
                status_code=200,
                mimetype="application/json"
            )
    except Exception as e:
        return func.HttpResponse(
            f"An error occurred: {str(e)}",
            status_code=500
        )

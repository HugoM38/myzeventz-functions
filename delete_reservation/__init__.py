import json
import azure.functions as func
import os
import pymongo

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Récupérer le nom de l'événement et l'email du participant à partir des paramètres de la requête
        event_name = req.params.get('event_name')
        participant_email = req.params.get('email')
        
        if not all([event_name, participant_email]):
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                event_name = req_body.get('event_name')
                participant_email = req_body.get('email')
           
        # Vérifier si le nom de l'événement et l'email du participant ont été fournis
        if not all([event_name, participant_email]):
            return func.HttpResponse(json.dumps({
                "reservations_deletion": "failed",
                "message": "Event name and email parameters are required."
                }), status_code=400)

        # Connexion à Cosmos DB
        client = pymongo.MongoClient(os.environ['COSMOS_DB_CONNECTION_STRING'])
        db = client['myzeventz-database']
        
        # Accéder à la collection de réservations
        reservations_collection = db['reservations']

        # Trouver et supprimer la réservation spécifique
        delete_result = reservations_collection.delete_one({
            "event_name": event_name,
            "participant": participant_email
        })

        if delete_result.deleted_count == 0:
            return func.HttpResponse(json.dumps({
                "reservations_deletion": "failed",
                "message": "Reservation not found or already deleted."
                }), status_code=404)

        # Renvoyer une confirmation de la suppression
        return func.HttpResponse(json.dumps({
            "reservations_deletion": "success",
            "message": "Reservation successfully deleted."
        }), status_code=200, mimetype='application/json')
    except Exception as e:
        return func.HttpResponse(f"Error deleting reservation: {str(e)}", status_code=500)

from flask import Flask, request, jsonify
import requests
import base64
import os
import uuid
from datetime import datetime

app = Flask(__name__)

@app.route('/v2/shipments/<shipment_id>/documents', methods=['POST'])
def upload_document(shipment_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        file_info = data.get('file')
        document_type_id = data.get('documentTypeId')

        if not file_info or not document_type_id:
            return jsonify({"error": "Missing required fields"}), 400

        # Guardar archivo PDF temporalmente desde base64
        file_name = f"{file_info['name']}_{uuid.uuid4().hex}.{file_info['extension']}"
        decoded_pdf = base64.b64decode(file_info['base64'])
        temp_path = os.path.join("temp", file_name)
        os.makedirs("temp", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(decoded_pdf)

        # Enviar el archivo a la API externa
        with open(temp_path, "rb") as pdf_file:
            response = requests.post(
                f"https://api.agentastra.ai/v2/shipments/{shipment_id}/documents",
                headers={
                    "Authorization": "Bearer aa_CliyrVLqQXA3ED7NCWfnSy5_6mlKBj7GJR8rqAa7mnY",
                    "accept": "application/json"
                },
                files={
                    "file": (file_name, pdf_file, "application/pdf"),
                    "documentTypeId": (None, document_type_id)
                }
            )

        # Borrar el archivo temporal
        os.remove(temp_path)

        # Devolver la respuesta de la API externa
        return jsonify({
            "external_api_status": response.status_code,
            "external_response": response.json()
        }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0"debug=True, port=port, threaded=True)

"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_cors import CORS
from utils import APIException, generate_sitemap
from datastructures import FamilyStructure

app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app)

jackson_family = FamilyStructure("Jackson")

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# Todos los miembros
@app.route('/members', methods=['GET'])
def get_all_members():
    members = jackson_family.get_all_members()
    return jsonify(members), 200

# miembro especifico
@app.route('/members/<int:id>', methods=['GET'])  # Corregido: /members en lugar de /member
def get_member(id):
    member = jackson_family.get_member(id)
    if member is None:
        return jsonify({"error": "Member not found"}), 404
    
    # Verificar que tiene todas las claves requeridas
    required_keys = ["id", "first_name", "age", "lucky_numbers"]
    if not all(key in member for key in required_keys):
        return jsonify({"error": "Member data incomplete"}), 500
    
    return jsonify(member), 200

# Agrega nuevo miembro 
@app.route('/members', methods=['POST'])  # Corregido: /members en lugar de /member
def add_member():
    member_data = request.get_json()
    if not member_data:
        return jsonify({"error": "Missing JSON body"}), 400
        
    # Validar campos obligatorios
    required_fields = ["first_name", "age", "lucky_numbers"]
    if not all(field in member_data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    # Crear nuevo miembro con estructura completa
    new_member = {
        "first_name": member_data["first_name"],
        "age": int(member_data["age"]),
        "lucky_numbers": member_data["lucky_numbers"]
    }
    
    # Agregar a la familia
    jackson_family.add_member(new_member)
    
    # Devolver el nuevo miembro creado (con ID generado)
    return jsonify(new_member), 200

# Elimina miembro de la familia
@app.route('/members/<int:id>', methods=['DELETE'])  
def delete_member(id):
    success = jackson_family.delete_member(id)
    if not success:
        return jsonify({"error": "Member not found"}), 404
    return jsonify({"done": True}), 200

# This only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
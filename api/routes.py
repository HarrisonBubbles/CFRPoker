from flask import request, jsonify
from api import api_blueprint
from src.mccfr import MCCFR
import pickle
import os

model_path = "mccfr_model"

try:
    with open(model_path, 'rb') as f:
        mccfr_model: MCCFR = pickle.load(f)
except FileNotFoundError:
    print(f"Warning: Model file {model_path} not found.")


@api_blueprint.route('/choose_move', methods=['POST'])
def choose_move():
    data = request.json
    
    infoset_key = data.get('infoset_key')
    
    if not infoset_key:
        return jsonify({'error': 'Missing required game state information'}), 400
    
    try:
        move = mccfr_model.choose_move(infoset_key)
    except:
        return jsonify({'error': "Invalid infoset provided."}), 400
    
    return jsonify({
        'action': move,
    })
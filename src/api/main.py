from flask import Flask, request, jsonify
import yaml
import uuid
from typing import Optional, Dict, Any
import sys
from flask_cors import CORS

sys.path.append('../wei_gen')

from wei_gen import WEIGen, Session
app = Flask(__name__)

CORS(app)

config_path = "../../config.yaml"
weigen = WEIGen(config_path)
sessions: Dict[str, Session] = {}


@app.route('/session/init', methods=['POST'])
def init():
    global weigen
    global sessions
    data = request.json
    user_session_id = data.get('session_id', '')
    cached_session = sessions.get(user_session_id, None)
    print("SS", user_session_id, cached_session)

    if cached_session: # load cached session
        print("loading cached session")
        session = cached_session 
    elif len(user_session_id) > 0: # load previous session from disk
        print("loading from disk", user_session_id, len(user_session_id) )
        session = weigen.new_session(user_session_id)
        sessions[user_session_id] = session
    else: # create a new session
        print("creating session", user_session_id)
        session = weigen.new_session()
        session_id = session.session_id
        sessions[session_id] = session
        data = request.json
        user_description = data.get('user_description', '')
        user_values = data.get('user_values', "")
        session.framework_step(user_description, user_values)
    

    try:
        return jsonify({"message": session.get_history()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/session/<session_id>/workflow_step', methods=['POST'])
def workflow_step(session_id):
    global sessions
    session = sessions.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    try:
        session.workflow_step()
        return jsonify({"message": session.get_history()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/session/<session_id>/code_step', methods=['POST'])
def code_step(session_id):
    global sessions
    session = sessions.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    try:
        session.code_step()
        return jsonify({"message":session.get_history()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/session/<session_id>/config_step', methods=['POST'])
def config_step(session_id):
    global sessions
    print("ss")
    session = sessions.get(session_id)
    print("ksjdahjkhsjakdsa")
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    try:
        print("sssssss2")
        session.config_step()
        return jsonify({"message": session.get_history()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/session/<session_id>/call_gen_env/<agent>', methods=['POST'])
def call_gen_env(session_id, agent):
    global sessions
   
    session = sessions.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    data = request.json
    print("Request Data:", data)  # Debugging print
    if not data:
        return jsonify({"error": "No JSON payload"}), 400

    user_msg = data.get('user_msg')
    print("User Message:", user_msg)  # Debugging print
    if user_msg is None:
        return jsonify({"error": "user_msg not found in request"}), 400

    try:
        response = session.call_gen_env(agent, user_msg)
        print("Response from call_gen_env:", response)  # Debugging print
        return jsonify({"response": session.get_history()}), 200
    except Exception as e:
        print("Exception occurred:", e)  # Debugging print
        return jsonify({"error": str(e)}), 400


    
@app.route('/session/<session_id>/history', methods=['GET'])
def get_history(session_id):
    global sessions
    session = sessions.get(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    history = session.get_history()
    return jsonify(history), 200

if __name__ == '__main__':
    app.run(debug=True)



# @app.route('/session/<session_id>/experiment', methods=['POST'])
# def execute_experiment(session_id):
#     global sessions
#     session = sessions.get(session_id)
#     if session is None:
#         return jsonify({"error": "Session not found"}), 404

#     data = request.json
#     user_description = data.get('user_description')
#     user_values = data.get('user_values', None)

#     try:
#         session.execute_experiment(user_description, user_values)
#         return jsonify({"message": "Experiment executed successfully"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 400

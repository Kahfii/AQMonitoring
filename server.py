from flask import Flask, request, jsonify
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)

client = MongoClient('mongodb+srv://erlinghaaland:ErlingHaalandGacor@cluster0.skwlxja.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0', server_api=ServerApi('1'))
db = client['sensor_data']
collection = db['readings']

@app.route('/post-data', methods=['POST'])
def post_data():
    if request.method == 'POST':
        data = request.json
        humidity = data.get('Humidity')
        temperature = data.get('Temperature')
        mq_value = data.get('MQ Value')
        
        if humidity is None or temperature is None or mq_value is None:
            return jsonify({'status': 'error', 'message': 'Invalid data'}), 400

    
        document = {
            'temp':  temperature,
            'humidity': humidity,
            'ppm': mq_value
        }
        collection.insert_one(document)
        return jsonify({'status': 'success', 'message': 'Data saved successfully'}), 201

@app.route('/get-data', methods=['GET'])
def get_data():
    
    data = collection.find({}, {"_id": 0})  
    return jsonify(list(data)), 200

if __name__ == '__main__':
    app.run(host='192.168.1.6', port=5000)

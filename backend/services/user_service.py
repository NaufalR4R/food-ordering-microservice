
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import certifi

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
MONGO_URI = "mongodb+srv://NaufalR4R:IaZEMLLoK0yexUuQ@cluster0.lstkg62.mongodb.net/?appName=Cluster0"

try:
    # Ambil path sertifikat dari certifi
    ca = certifi.where()

    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=ca,  # GUNAKAN INI daripada tlsAllowInvalidCertificates
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000
    )
    
    # Test connection
    client.admin.command('ping')
    print("✅ Berhasil terhubung ke MongoDB Atlas!")
    
    db = client['user_service']
    user_collection = db['users']
    
    # Insert sample user jika collection kosong
    if user_collection.count_documents({}) == 0:
        sample_user = {
            "nama": "John Doe",
            "email": "john@example.com",
            "phone": "08123456789",
            "address": "Jl. Contoh No. 123, Jakarta",
            "created_at": datetime.utcnow()
        }
        user_collection.insert_one(sample_user)
        print("✅ Sample user data inserted successfully")
    
    print("✅ Connected to MongoDB - User Service")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Helper function
def serialize_doc(doc):
    if doc:
        doc['_id'] = str(doc['_id'])
        if 'created_at' in doc and isinstance(doc['created_at'], datetime):
            doc['created_at'] = doc['created_at'].isoformat()
    return doc

# Endpoint untuk get semua users
@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = list(user_collection.find().sort("created_at", -1))
        
        # Convert ObjectId and datetime to string
        for user in users:
            serialize_doc(user)
        
        return jsonify({
            'server': 'User Service (Port 5003)',
            'data': users,
            'count': len(users)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk get user by ID
@app.route('/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = user_collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify({
                'server': 'User Service (Port 5003)',
                'data': serialize_doc(user)
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk get user by email
@app.route('/users/email/<email>', methods=['GET'])
def get_user_by_email(email):
    try:
        user = user_collection.find_one({"email": email})
        if user:
            return jsonify({
                'server': 'User Service (Port 5003)',
                'data': serialize_doc(user)
            }), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk register user
@app.route('/users', methods=['POST'])
def register_user():
    try:
        data = request.json
        
        # Validasi required fields
        required_fields = ['nama', 'email', 'phone']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Cek apakah email sudah terdaftar
        existing_user = user_collection.find_one({"email": data['email']})
        if existing_user:
            return jsonify({'error': 'Email already registered'}), 400
        
        user = {
            "nama": data['nama'],
            "email": data['email'],
            "phone": data['phone'],
            "address": data.get('address', ''),
            "created_at": datetime.utcnow()
        }
        
        result = user_collection.insert_one(user)
        
        return jsonify({
            'message': 'User berhasil terdaftar di User Service',
            'user_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk update user
@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.json
        
        # Jika update email, cek apakah email sudah dipakai user lain
        if 'email' in data:
            existing_user = user_collection.find_one({
                "email": data['email'],
                "_id": {"$ne": ObjectId(user_id)}
            })
            if existing_user:
                return jsonify({'error': 'Email already used by another user'}), 400
        
        result = user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'User berhasil diupdate'}), 200
        else:
            return jsonify({'error': 'User not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk delete user
@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = user_collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'User berhasil dihapus'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk user statistics
@app.route('/users/stats', methods=['GET'])
def get_user_stats():
    try:
        total_users = user_collection.count_documents({})
        
        # Get latest registered users
        latest_users = list(user_collection.find().sort("created_at", -1).limit(5))
        for user in latest_users:
            serialize_doc(user)
        
        return jsonify({
            'server': 'User Service (Port 5003)',
            'stats': {
                'total_users': total_users,
                'latest_users': latest_users
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'User Service',
        'port': 5003
    }), 200

if __name__ == '__main__':
    print("🚀 Starting User Service on port 5003...")
    app.run(host='0.0.0.0', port=5003, debug=True)

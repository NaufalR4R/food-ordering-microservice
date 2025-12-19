
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import json
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
    
    db = client['order_service']
    order_collection = db['orders']
    print("✅ Connected to MongoDB - Order Service")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Helper function
def serialize_doc(doc):
    if doc:
        doc['_id'] = str(doc['_id'])
        # Convert datetime to string
        if 'created_at' in doc and isinstance(doc['created_at'], datetime):
            doc['created_at'] = doc['created_at'].isoformat()
    return doc

# Endpoint untuk get semua orders
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        status = request.args.get('status')
        
        if status:
            orders = list(order_collection.find({"status": status}).sort("created_at", -1))
        else:
            orders = list(order_collection.find().sort("created_at", -1))
        
        # Convert ObjectId and datetime to string
        for order in orders:
            serialize_doc(order)
        
        return jsonify({
            'server': 'Order Service (Port 5002)',
            'data': orders,
            'count': len(orders)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk get order by ID
@app.route('/orders/<order_id>', methods=['GET'])
def get_order_by_id(order_id):
    try:
        order = order_collection.find_one({"_id": ObjectId(order_id)})
        if order:
            return jsonify({
                'server': 'Order Service (Port 5002)',
                'data': serialize_doc(order)
            }), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk create order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.json
        
        # Validasi required fields
        required_fields = ['customer_name', 'phone', 'address', 'menu_items', 'total_amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        order = {
            "customer_name": data['customer_name'],
            "phone": data['phone'],
            "address": data['address'],
            "menu_items": data['menu_items'],  # Array of {menu_id, nama, qty, harga}
            "total_amount": float(data['total_amount']),
            "payment_method": data.get('payment_method', 'COD'),
            "status": "pending",
            "created_at": datetime.utcnow()
        }
        
        result = order_collection.insert_one(order)
        
        return jsonify({
            'message': 'Order berhasil dibuat di Order Service',
            'order_id': str(result.inserted_id),
            'status': 'pending'
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk update order status
@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.json
        
        if 'status' not in data:
            return jsonify({'error': 'Missing status field'}), 400
        
        valid_statuses = ['pending', 'processing', 'completed', 'cancelled']
        if data['status'] not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        
        result = order_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": data['status']}}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'message': 'Order status berhasil diupdate',
                'status': data['status']
            }), 200
        else:
            return jsonify({'error': 'Order not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk update order
@app.route('/orders/<order_id>', methods=['PUT'])
def update_order(order_id):
    try:
        data = request.json
        result = order_collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Order berhasil diupdate'}), 200
        else:
            return jsonify({'error': 'Order not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk delete order
@app.route('/orders/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    try:
        result = order_collection.delete_one({"_id": ObjectId(order_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Order berhasil dihapus'}), 200
        else:
            return jsonify({'error': 'Order not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk statistik
@app.route('/orders/stats', methods=['GET'])
def get_order_stats():
    try:
        total_orders = order_collection.count_documents({})
        pending = order_collection.count_documents({"status": "pending"})
        processing = order_collection.count_documents({"status": "processing"})
        completed = order_collection.count_documents({"status": "completed"})
        cancelled = order_collection.count_documents({"status": "cancelled"})
        
        # Calculate total revenue from completed orders
        pipeline = [
            {"$match": {"status": "completed"}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$total_amount"}}}
        ]
        revenue_result = list(order_collection.aggregate(pipeline))
        total_revenue = revenue_result[0]['total_revenue'] if revenue_result else 0
        
        return jsonify({
            'server': 'Order Service (Port 5002)',
            'stats': {
                'total_orders': total_orders,
                'pending': pending,
                'processing': processing,
                'completed': completed,
                'cancelled': cancelled,
                'total_revenue': total_revenue
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Order Service',
        'port': 5002
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Order Service on port 5002...")
    app.run(host='0.0.0.0', port=5002, debug=True)

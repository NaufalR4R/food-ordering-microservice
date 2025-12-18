
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson import ObjectId
import os

app = Flask(__name__)
CORS(app)

# MongoDB Configuration
# Ganti dengan connection string Anda
MONGO_URI = "mongodb+srv://verilita75_db_user:<db_password>@cluster0.lstkg62.mongodb.net/?appName=Cluster0"

try:
    client = MongoClient(MONGO_URI)
    db = client['menu_service']
    menu_collection = db['menu']
    
    # Insert sample data jika collection kosong
    if menu_collection.count_documents({}) == 0:
        sample_menu = [
            {
                "nama_menu": "Nasi Goreng Spesial",
                "kategori": "Makanan",
                "harga": 25000,
                "deskripsi": "Nasi goreng dengan telur dan ayam",
                "gambar_url": "https://via.placeholder.com/300x200/FF5733/FFFFFF?text=Nasi+Goreng",
                "tersedia": True
            },
            {
                "nama_menu": "Mie Goreng",
                "kategori": "Makanan",
                "harga": 20000,
                "deskripsi": "Mie goreng pedas manis",
                "gambar_url": "https://via.placeholder.com/300x200/FFC300/FFFFFF?text=Mie+Goreng",
                "tersedia": True
            },
            {
                "nama_menu": "Ayam Geprek",
                "kategori": "Makanan",
                "harga": 28000,
                "deskripsi": "Ayam goreng dengan sambal geprek",
                "gambar_url": "https://via.placeholder.com/300x200/C70039/FFFFFF?text=Ayam+Geprek",
                "tersedia": True
            },
            {
                "nama_menu": "Es Teh Manis",
                "kategori": "Minuman",
                "harga": 5000,
                "deskripsi": "Teh manis dingin segar",
                "gambar_url": "https://via.placeholder.com/300x200/28B463/FFFFFF?text=Es+Teh",
                "tersedia": True
            },
            {
                "nama_menu": "Jus Alpukat",
                "kategori": "Minuman",
                "harga": 15000,
                "deskripsi": "Jus alpukat segar",
                "gambar_url": "https://via.placeholder.com/300x200/58D68D/FFFFFF?text=Jus+Alpukat",
                "tersedia": True
            },
            {
                "nama_menu": "Pisang Goreng",
                "kategori": "Snack",
                "harga": 12000,
                "deskripsi": "Pisang goreng crispy",
                "gambar_url": "https://via.placeholder.com/300x200/F39C12/FFFFFF?text=Pisang+Goreng",
                "tersedia": True
            }
        ]
        menu_collection.insert_many(sample_menu)
        print("✅ Sample menu data inserted successfully")
    
    print("✅ Connected to MongoDB - Menu Service")
except Exception as e:
    print(f"❌ MongoDB Connection Error: {e}")

# Helper function to convert ObjectId to string
def serialize_doc(doc):
    if doc:
        doc['_id'] = str(doc['_id'])
    return doc

# Endpoint untuk get semua menu
@app.route('/menu', methods=['GET'])
def get_menu():
    try:
        kategori = request.args.get('kategori')
        
        if kategori and kategori != 'Semua':
            menu = list(menu_collection.find({"kategori": kategori}))
        else:
            menu = list(menu_collection.find())
        
        # Convert ObjectId to string
        for item in menu:
            item['_id'] = str(item['_id'])
        
        return jsonify({
            'server': 'Menu Service (Port 5001)',
            'data': menu,
            'count': len(menu)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk get menu by ID
@app.route('/menu/<menu_id>', methods=['GET'])
def get_menu_by_id(menu_id):
    try:
        menu = menu_collection.find_one({"_id": ObjectId(menu_id)})
        if menu:
            return jsonify({
                'server': 'Menu Service (Port 5001)',
                'data': serialize_doc(menu)
            }), 200
        else:
            return jsonify({'error': 'Menu not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk add menu
@app.route('/menu', methods=['POST'])
def add_menu():
    try:
        data = request.json
        
        # Validasi required fields
        required_fields = ['nama_menu', 'kategori', 'harga']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        menu_item = {
            "nama_menu": data['nama_menu'],
            "kategori": data['kategori'],
            "harga": float(data['harga']),
            "deskripsi": data.get('deskripsi', ''),
            "gambar_url": data.get('gambar_url', ''),
            "tersedia": data.get('tersedia', True)
        }
        
        result = menu_collection.insert_one(menu_item)
        
        return jsonify({
            'message': 'Menu berhasil ditambahkan di Menu Service',
            'menu_id': str(result.inserted_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk update menu
@app.route('/menu/<menu_id>', methods=['PUT'])
def update_menu(menu_id):
    try:
        data = request.json
        result = menu_collection.update_one(
            {"_id": ObjectId(menu_id)},
            {"$set": data}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Menu berhasil diupdate'}), 200
        else:
            return jsonify({'error': 'Menu not found or no changes made'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint untuk delete menu
@app.route('/menu/<menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    try:
        result = menu_collection.delete_one({"_id": ObjectId(menu_id)})
        
        if result.deleted_count > 0:
            return jsonify({'message': 'Menu berhasil dihapus'}), 200
        else:
            return jsonify({'error': 'Menu not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'Menu Service',
        'port': 5001
    }), 200

if __name__ == '__main__':
    print("🚀 Starting Menu Service on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=True)

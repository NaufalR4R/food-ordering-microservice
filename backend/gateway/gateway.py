from flask import Flask, request, jsonify

from flask_cors import CORS
from flask_compress import Compress
import requests
import time

app = Flask(__name__)
CORS(app)
Compress(app)  # Enable compression untuk save bandwidth

# Daftar backend servers untuk setiap service
MENU_SERVERS = [
    'http://110.239.67.173:5001'
]

ORDER_SERVERS = [
    'http://110.239.67.173:5002'
]

USER_SERVERS = [
    'http://110.239.67.173:5003'
]

# Round-robin counters
menu_counter = 0
order_counter = 0
user_counter = 0

# Load balancing dengan health check
def get_healthy_server(servers, counter_name):
    global menu_counter, order_counter, user_counter
    
    # Get current counter
    if counter_name == 'menu':
        current = menu_counter
    elif counter_name == 'order':
        current = order_counter
    else:
        current = user_counter
    
    # Try each server in round-robin fashion
    for i in range(len(servers)):
        server_index = (current + i) % len(servers)
        server = servers[server_index]
        
        try:
            # Health check
            response = requests.get(f"{server}/health", timeout=2)
            if response.status_code == 200:
                # Update counter for next request
                if counter_name == 'menu':
                    menu_counter = (server_index + 1) % len(servers)
                elif counter_name == 'order':
                    order_counter = (server_index + 1) % len(servers)
                else:
                    user_counter = (server_index + 1) % len(servers)
                
                print(f"✅ Connected to {server} ({counter_name} service)")
                return server
        except:
            print(f"❌ {server} is down, trying next...")
            continue
    
    return None

# ============= MENU ENDPOINTS =============

@app.route('/api/menu', methods=['GET'])
def get_menu():
    server = get_healthy_server(MENU_SERVERS, 'menu')
    
    if server is None:
        return jsonify({
            'error': 'Menu service tidak tersedia',
            'message': 'Semua menu server sedang down'
        }), 503
    
    try:
        kategori = request.args.get('kategori')
        params = {'kategori': kategori} if kategori else {}
        
        response = requests.get(f"{server}/menu", params=params, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu/<menu_id>', methods=['GET'])
def get_menu_by_id(menu_id):
    server = get_healthy_server(MENU_SERVERS, 'menu')
    
    if server is None:
        return jsonify({'error': 'Menu service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/menu/{menu_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu', methods=['POST'])
def add_menu():
    server = get_healthy_server(MENU_SERVERS, 'menu')
    
    if server is None:
        return jsonify({'error': 'Menu service tidak tersedia'}), 503
    
    try:
        response = requests.post(f"{server}/menu", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu/<menu_id>', methods=['PUT'])
def update_menu(menu_id):
    server = get_healthy_server(MENU_SERVERS, 'menu')
    
    if server is None:
        return jsonify({'error': 'Menu service tidak tersedia'}), 503
    
    try:
        response = requests.put(f"{server}/menu/{menu_id}", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/menu/<menu_id>', methods=['DELETE'])
def delete_menu(menu_id):
    server = get_healthy_server(MENU_SERVERS, 'menu')
    
    if server is None:
        return jsonify({'error': 'Menu service tidak tersedia'}), 503
    
    try:
        response = requests.delete(f"{server}/menu/{menu_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= ORDER ENDPOINTS =============

@app.route('/api/orders', methods=['GET'])
def get_orders():
    server = get_healthy_server(ORDER_SERVERS, 'order')
    
    if server is None:
        return jsonify({'error': 'Order service tidak tersedia'}), 503
    
    try:
        status = request.args.get('status')
        params = {'status': status} if status else {}
        
        response = requests.get(f"{server}/orders", params=params, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order_by_id(order_id):
    server = get_healthy_server(ORDER_SERVERS, 'order')
    
    if server is None:
        return jsonify({'error': 'Order service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/orders/{order_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    server = get_healthy_server(ORDER_SERVERS, 'order')
    
    if server is None:
        return jsonify({'error': 'Order service tidak tersedia'}), 503
    
    try:
        response = requests.post(f"{server}/orders", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    server = get_healthy_server(ORDER_SERVERS, 'order')
    
    if server is None:
        return jsonify({'error': 'Order service tidak tersedia'}), 503
    
    try:
        response = requests.put(f"{server}/orders/{order_id}/status", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/stats', methods=['GET'])
def get_order_stats():
    server = get_healthy_server(ORDER_SERVERS, 'order')
    
    if server is None:
        return jsonify({'error': 'Order service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/orders/stats", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= USER ENDPOINTS =============

@app.route('/api/users', methods=['GET'])
def get_users():
    server = get_healthy_server(USER_SERVERS, 'user')
    
    if server is None:
        return jsonify({'error': 'User service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/users", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    server = get_healthy_server(USER_SERVERS, 'user')
    
    if server is None:
        return jsonify({'error': 'User service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/users/{user_id}", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['POST'])
def register_user():
    server = get_healthy_server(USER_SERVERS, 'user')
    
    if server is None:
        return jsonify({'error': 'User service tidak tersedia'}), 503
    
    try:
        response = requests.post(f"{server}/users", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    server = get_healthy_server(USER_SERVERS, 'user')
    
    if server is None:
        return jsonify({'error': 'User service tidak tersedia'}), 503
    
    try:
        response = requests.put(f"{server}/users/{user_id}", json=request.json, timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/stats', methods=['GET'])
def get_user_stats():
    server = get_healthy_server(USER_SERVERS, 'user')
    
    if server is None:
        return jsonify({'error': 'User service tidak tersedia'}), 503
    
    try:
        response = requests.get(f"{server}/users/stats", timeout=5)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============= GATEWAY INFO =============

@app.route('/', methods=['GET'])
def gateway_info():
    return jsonify({
        'service': 'API Gateway',
        'version': '1.0',
        'endpoints': {
            'menu': '/api/menu',
            'orders': '/api/orders',
            'users': '/api/users'
        },
        'features': [
            'Load Balancing (Round Robin)',
            'Automatic Failover',
            'Health Check',
            'Response Compression'
        ]
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    # Check all services
    services_status = {
        'menu': False,
        'order': False,
        'user': False
    }
    
    for server in MENU_SERVERS:
        try:
            requests.get(f"{server}/health", timeout=1)
            services_status['menu'] = True
            break
        except:
            pass
    
    for server in ORDER_SERVERS:
        try:
            requests.get(f"{server}/health", timeout=1)
            services_status['order'] = True
            break
        except:
            pass
    
    for server in USER_SERVERS:
        try:
            requests.get(f"{server}/health", timeout=1)
            services_status['user'] = True
            break
        except:
            pass
    
    all_healthy = all(services_status.values())
    
    return jsonify({
        'status': 'healthy' if all_healthy else 'degraded',
        'gateway': 'online',
        'services': services_status
    }), 200 if all_healthy else 503

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Starting API Gateway on port 5000...")
    print("=" * 60)
    print("\n📡 Backend Services:")
    print(f"   Menu Service:  {MENU_SERVERS}")
    print(f"   Order Service: {ORDER_SERVERS}")
    print(f"   User Service:  {USER_SERVERS}")
    print("\n✨ Features:")
    print("   - Load Balancing (Round Robin)")
    print("   - Automatic Failover")
    print("   - Health Check")
    print("   - Response Compression")
    print("\n🌐 Access Gateway at: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

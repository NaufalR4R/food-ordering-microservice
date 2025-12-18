# 🍔 Food Ordering Microservice System

Sistem pemesanan makanan online berbasis microservice architecture menggunakan Flask, MongoDB, dan API Gateway dengan load balancing.

## 📋 Features
- 3 Independent Services (Menu, Order, User)
- API Gateway dengan Load Balancing
- Fault Tolerance & High Availability
- MongoDB Database
- Modern Web Frontend

## 🛠️ Tech Stack
- **Backend**: Python Flask
- **Database**: MongoDB
- **Frontend**: HTML, CSS, JavaScript
- **API**: RESTful API

## 📂 Project Structure
```
food-ordering-microservice/
├── backend/
│   ├── services/
│   │   ├── menu_service.py
│   │   ├── order_service.py
│   │   └── user_service.py
│   ├── gateway/
│   │   └── gateway.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── docs/
│   ├── API_Documentation.md
│   ├── Setup_Guide.md
│   └── Architecture.md
├── tests/
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB (Atlas atau Local)

### Installation

1. Clone repository
\`\`\`bash
git clone <repository-url>
cd food-ordering-microservice
\`\`\`

2. Setup virtual environment
\`\`\`bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
\`\`\`

3. Configure MongoDB
- Edit connection string di setiap service
- Update `MONGO_URI` variable

4. Run Services
\`\`\`bash
# Terminal 1
python services/menu_service.py

# Terminal 2
python services/order_service.py

# Terminal 3
python services/user_service.py

# Terminal 4
python gateway/gateway.py
\`\`\`

5. Access Application
- Frontend: http://localhost:3000
- Gateway: http://localhost:5000
- Menu Service: http://localhost:5001
- Order Service: http://localhost:5002
- User Service: http://localhost:5003

## 📡 API Endpoints

### Gateway (Port 5000)
\`\`\`
GET    /api/menu          - Get all menu items
POST   /api/menu          - Add new menu item
GET    /api/orders        - Get all orders
POST   /api/orders        - Create new order
GET    /api/users         - Get all users
POST   /api/users         - Register new user
\`\`\`

## 🏗️ Architecture
```
Frontend → Gateway → [Menu Service, Order Service, User Service] → MongoDB
```

- **Load Balancing**: Round-robin distribution
- **Fault Tolerance**: Automatic failover
- **Database**: Isolated per service

## 📖 Documentation
- [Setup Guide](docs/Setup_Guide.md)
- [API Documentation](docs/API_Documentation.md)
- [Architecture Details](docs/Architecture.md)

## 👨‍💻 Author
[Nama Anda] - [NIM]

## 📝 License
This project is for educational purposes.

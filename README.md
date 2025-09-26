# Order Management System

##  Features
```
Customer Management
Order Management
Notifications
```
## Clone Repository
```bash
git clone https://github.com/your-username/order-management.git
cd order-management
```

## Create Virtual Environment & Install Dependencies
```python
python -m venv .venv
source .venv/bin/activate   
pip install --upgrade pip
pip install -r requirements.txt')
```

## Database Setup
```
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'order_management',
    'USER': 'postgres',
    'PASSWORD': 'password',
    'HOST': 'localhost',
    'PORT': '5432',
  }
}
```

## Run migrations
```
python manage.py makemigrations
python manage.py migrate
```

## Create Superuser
```
python manage.py createsuperuser
```
## Authentication (OAuth2)
### POST /api/customers/register/
```
POST /api/customers/register/
{
  "email": "test@mail.com",
  "first_name": "John",
  "last_name": "James",
  "phone": "+254700000000",
  "address": "Utawala, Kenya",
  "password": "1234"
}
```
### Token authorization
```
POST /o/token/
{
  "email": "test@mail.com",
  "password": "1234"
}
```
## Docker Setup
###Build Image
```
docker build -t order-management:latest .
```
###Run Container
```
docker run -p 8000:8000 order-management:latest
```
### Kubernetes (Kind)
#### Create Cluster
```
kind create cluster --name order-cluster
```
#### Load Image
```
kind load docker-image order-management:latest --name order-cluster
```
#### Deploy
```
kubectl apply -f deployment.yaml
kubectl get pods
```

#### Access Service
```
kubectl port-forward service/order-management 8000:8000
```



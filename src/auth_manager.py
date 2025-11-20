import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import secrets

SECRET_KEY = os.getenv('JWT_SECRET_KEY', secrets.token_hex(32))
ALGORITHM = 'HS256'
TOKEN_EXPIRY_HOURS = 24

def generate_token(user_id: str, user_data: dict = None) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS),
        'iat': datetime.utcnow()
    }
    
    if user_data:
        payload['user_data'] = user_data
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {'valid': True, 'payload': payload}
    except jwt.ExpiredSignatureError:
        return {'valid': False, 'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'valid': False, 'error': 'Invalid token'}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'status': 'error', 'message': 'Invalid token format'}), 401
        
        if not token:
            user_id = request.json.get('user_id') if request.json else None
            if user_id:
                return f(*args, **kwargs)
            return jsonify({'status': 'error', 'message': 'Token required'}), 401
        
        result = verify_token(token)
        if not result['valid']:
            return jsonify({'status': 'error', 'message': result['error']}), 401
        
        request.user_id = result['payload']['user_id']
        return f(*args, **kwargs)
    
    return decorated

def optional_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
                result = verify_token(token)
                if result['valid']:
                    request.user_id = result['payload']['user_id']
            except:
                pass
        
        return f(*args, **kwargs)
    
    return decorated

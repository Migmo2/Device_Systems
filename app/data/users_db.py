"""Base de datos en memoria para el recurso users."""

fake_users_db = {
    1: {"id": 1, "name": "Admin Usuario", "email": "admin@device-systems.com", "role": "admin", "is_active": True},
    2: {"id": 2, "name": "Support Usuario", "email": "support@device-systems.com", "role": "support", "is_active": True},
    3: {"id": 3, "name": "Usuario Normal", "email": "user@device-systems.com", "role": "user", "is_active": False},
}

next_user_id = 4
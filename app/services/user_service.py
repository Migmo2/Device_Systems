"""Logica de negocio para usuarios."""

from typing import Optional

from app.data.users_db import fake_users_db


def list_users(role: Optional[str] = None, is_active: Optional[bool] = None):
    users = list(fake_users_db.values())
    if role is not None:
        users = [user for user in users if user["role"] == role]
    if is_active is not None:
        users = [user for user in users if user["is_active"] == is_active]
    return users


def email_exists(email: str, exclude_user_id: Optional[int] = None) -> bool:
    normalized_email = email.lower()
    return any(
        user["email"].lower() == normalized_email
        and user["id"] != exclude_user_id
        for user in fake_users_db.values()
    )


def create_user(user_data: dict) -> dict:
    from app.data import users_db

    user = {"id": users_db.next_user_id, **user_data}
    fake_users_db[users_db.next_user_id] = user
    users_db.next_user_id += 1
    return user


def replace_user(user_id: int, user_data: dict) -> dict:
    fake_users_db[user_id].update(user_data)
    return fake_users_db[user_id]


def update_user(user_id: int, user_data: dict) -> dict:
    fake_users_db[user_id].update(user_data)
    return fake_users_db[user_id]


def delete_user(user_id: int) -> None:
    del fake_users_db[user_id]
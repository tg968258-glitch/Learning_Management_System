from pwdlib import PasswordHash

from Backend.src.services.filehandler import USERS_FILE, load_data, save_data

password_hash = PasswordHash.recommended()


def register_user(username, email, password, role):

    users = load_data(USERS_FILE)

  
    for user in users:
        if user["email"] == email:
            raise ValueError("User with this email already exists")

        if user["username"] == username:
            raise ValueError("Username already exists")

    
    if users:
        user_id = max(user["user_id"] for user in users) + 1
    else:
        user_id = 1

    hashed_password = password_hash.hash(password)

    user = {
        "user_id": user_id,
        "username": username,
        "email": email,
        "password_hash": hashed_password,
        "role": role
    }

    users.append(user)

    save_data(USERS_FILE, users)

    return {
        "user_id": user_id,
        "username": username,
        "email": email,
        "role": role
    }


def authenticate_user(email, password):

    users = load_data(USERS_FILE)

    for user in users:

        if user["email"] == email:

            if password_hash.verify(
                password,
                user["password_hash"]
            ):
                return user

            return None

    return None
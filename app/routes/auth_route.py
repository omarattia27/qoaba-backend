
from fastapi import APIRouter, Response, status
from app.models.user_model import User
from app.schemas.user_schema import user_serializer
from app.config.database import user_collection
from app.utils.encryption import encrypt_password, generate_salt, check_password
from app.utils.gravatar import generate_random_avatar_url
from bson import ObjectId

auth_api_router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found DEMO for deployment"}},
)


@auth_api_router.post("/login")
async def user_authenticate(user: User, response: Response):
    user_db = user_collection.find_one({"email": user.email})

    if user_db is None:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "User not authenticated"

    if check_password(user.password, user_db["password"], user_db["salt"]):
        user_data = [
            user_db["username"],
            user_db["picture"],
            user_db["role"],
            str(user_db["_id"]),
        ]
        return user_data
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "User not authenticated"


@auth_api_router.post("/")
async def user_signup(user: User, response: Response):
    password = user.password
    # Check if user already exists
    user_in_db = user_collection.find_one({"email": user.email})
    if user_in_db is not None:
        response.status_code = status.HTTP_409_CONFLICT
        return "User already exists"

    # Generate avatar url
    user.picture = generate_random_avatar_url(user.email)

    # Set user role
    user.role = "user"

    # Generate salt
    salt = generate_salt()
    hashed_password = encrypt_password(password, salt)
    user.password = hashed_password
    user.salt = salt

    user_collection.insert_one(dict(user))
    return user_collection.find_one({"email": user.email})["email"]


@auth_api_router.put("/{id}/username")
async def username_update(id: str, user: User, response: Response):
    user_in_db = user_collection.find_one({"username": user.username})
    if user_in_db is not None:
        response.status_code = status.HTTP_409_CONFLICT
        return "User already exists"

    user_collection.find_one_and_update({"_id": ObjectId(id)}, {
    "$set": {"username": user.username}
    })
    return "Username updated"


@auth_api_router.put("/{id}/email")
async def email_update(id: str, user: User, response: Response):
    email_in_db = user_collection.find_one({"email": user.email})
    if email_in_db is not None:
        response.status_code = status.HTTP_409_CONFLICT
        return "Email already exists"

    user_db = user_collection.find_one({"_id": ObjectId(id)})
    if check_password(user.password, user_db["password"], user_db["salt"]):
        user_collection.find_one_and_update({"_id": ObjectId(id)}, {
        "$set": {"email": user.email}
        })
        return "Email updated"
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "User not authenticated"
    

@auth_api_router.put("/{id}/password")
async def password_update(id: str, user: User, response: Response):
    current_password = user.password.split(" ")[0]
    new_password = user.password.split(" ")[1]
    
    user_db = user_collection.find_one({"_id": ObjectId(id)})
    if check_password(current_password, user_db["password"], user_db["salt"]):
        salt = generate_salt()
        hashed_password = encrypt_password(new_password, salt)

        user_collection.find_one_and_update({"_id": ObjectId(id)}, {
        "$set": {"password": hashed_password, "salt": salt}
        })
        return "Password updated"
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "User not authenticated"
    

@auth_api_router.delete("/{id}")
async def user_delete(id: str, user: User, response: Response):
    user_db = user_collection.find_one({"_id": ObjectId(id)})
    if check_password(user.password, user_db["password"], user_db["salt"]) and user_db["email"] == user.email:
        user_collection.find_one_and_delete({"_id": ObjectId(id)})
        return "User deleted"
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return "User not authenticated"

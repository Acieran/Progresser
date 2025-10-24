from fastapi import APIRouter

users_router = APIRouter(tags=["users"])

@users_router.get("/users")
async def get_users():
    return {"users": []}
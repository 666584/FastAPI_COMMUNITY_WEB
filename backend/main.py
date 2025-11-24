from fastapi import FastAPI
from routers.user_router import router as user_router
from routers.post_router import router as post_router
from routers.comment_router import router as comment_router
from routers.ai_chat_router import router as ai_chat_router
from database import test_connection, Base, engine

app = FastAPI()
app.include_router(user_router)
app.include_router(post_router)
app.include_router(comment_router)
app.include_router(ai_chat_router)


@app.get("/db-check")
def check_db():
    try:
        result = test_connection()
        return {"status": "OK", "result": str(result)}
    except Exception as e:
        return {"status": "FAILED", "error": str(e)}

Base.metadata.create_all(bind=engine)
#uvicorn main:app --reload
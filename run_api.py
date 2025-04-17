from project.api.routes.transactions import router as transactions_router
from project.api.routes.users import router as user_router
from project.api.routes.categories import router as category_router

from fastapi import FastAPI
import uvicorn

app = FastAPI()
app.include_router(transactions_router)
app.include_router(user_router)
app.include_router(category_router)

if __name__ == "__main__":
   

    uvicorn.run(app, host="0.0.0.0", port=8000)
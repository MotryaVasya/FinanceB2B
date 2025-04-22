from project.api.routes.transactions import router as transactions_router
from project.api.routes.users import router as user_router
from project.api.routes.categories import router as category_router
from project.db.session import init_db_on_start_up
from fastapi import FastAPI
import uvicorn

from project import on_startup, on_shutdown

app = FastAPI(on_startup=[on_startup, init_db_on_start_up],
               on_shutdown=[on_shutdown])

app.include_router(transactions_router)
app.include_router(user_router)
app.include_router(category_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
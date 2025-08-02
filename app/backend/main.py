from fastapi import FastAPI
from .routers import crew_router as crew
from .routers import rag_router as rag
from .routers import document_router as parse
from .routers import database_router as store
from .routers import validate_router as validate


app = FastAPI()

app.include_router(parse.router, prefix="/parse")
app.include_router(crew.router, prefix="/crew")
app.include_router(rag.router, prefix="/rag")
app.include_router(store.router, prefix="/store")
app.include_router(validate.router, prefix="/validate")

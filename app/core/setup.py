from typing import Any, AsyncGenerator, Callable
from contextlib import _AsyncGeneratorContextManager, asynccontextmanager
from fastapi import APIRouter, FastAPI
from app.core.config import AppSettings, PostgresSettings
from app.core.db.database import engine, Base

async def create_tables() -> None:
    try:
        async with engine.begin() as conn:
            print("Starting table creation...")
            await conn.run_sync(Base.metadata.create_all)
            print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")


def applifespan_factory(
    settings: AppSettings,
    create_tables_on_start: bool = True
) -> Callable[[FastAPI], _AsyncGeneratorContextManager[Any]]:

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator:
        if isinstance(settings, PostgresSettings) and create_tables_on_start:
            await create_tables()
        
        yield
        
        await engine.dispose()
    
    return lifespan
     
def create_application(
    api_router: APIRouter,
    ws_router: APIRouter,
    settings: AppSettings,
    create_tables_on_start: bool = True,
    **kwargs: Any,
) -> FastAPI:   
    lifespan = applifespan_factory(settings, create_tables_on_start=create_tables_on_start)
    
    application = FastAPI(lifespan=lifespan, **kwargs)
    
    application.include_router(api_router)
    
    # async def websocket_auth_middleware(scope, receive, send):
    #     # print(f"scope: {scope.get("path")}")
    #     if scope["type"] == "websocket":
    #         print("WebSocket connection received.")
    #         print(application.router.routes)
    #         for route in application.routes:
    #             if route.path == scope["path"]:
    #                 await route.endpoint(StarletteWebSocket(scope, receive, send))
    #                 return
    #         # await application.router.routes[2].endpoint(StarletteWebSocket(scope, receive, send)) #Routes[2] is the websocket route.            
    #         # return

    #     await application(scope, receive, send)

    # application.add_middleware(lambda app: lambda scope, receive, send: websocket_auth_middleware(scope, receive, send))
    application.include_router(ws_router)
    
    return application
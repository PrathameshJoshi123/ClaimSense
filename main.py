from fastapi import FastAPI
from services.user_service.src.api.user_routes import router
from services.user_service.src.middleware.logging_middleware import LoggingMiddleware
from services.user_service.src.middleware.error_handler import ErrorHandlerMiddleware
from services.policy_intelligence_service.api.v1.upload import router as upload_router
from services.policy_intelligence_service.api.v1.policies import router as policies_router
from services.policy_intelligence_service.api.v1.chat import router as chat_router  # Add chat router import
from services.shadow_claim_simulator.routes.simulation import router as simulation_router
from services.policy_recommendation_service.api.policy_api import router as policy_recommendation_router

app = FastAPI(title="Dreamflow Backend", version="1.0.0")
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlerMiddleware)
app.include_router(router)
app.include_router(upload_router, prefix="/policy", tags=["policy"])
app.include_router(policies_router, prefix="/policy", tags=["policy"])
app.include_router(chat_router, prefix="/policy", tags=["policy"])  # Add chat router
app.include_router(simulation_router, prefix="/shadow-claim", tags=["shadow-claim"])
app.include_router(policy_recommendation_router, prefix="/policy-recommendation", tags=["policy-recommendation"])

@app.get("/")
async def root():
    return {"message": "Welcome to the ClaimSense Backend API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_vulnerability_stats
import uvicorn

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/stats")
async def get_stats():
    return get_vulnerability_stats()

@app.get("/api/vulnerabilities")
async def get_vulnerabilities(limit: int = 100):
    return get_vulnerabilities_from_db(limit)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
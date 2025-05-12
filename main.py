from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from radio_scraper import scrape_stations

app = FastAPI()

# Allow all CORS (frontend on 8080)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/stations")
async def get_stations():
    return await scrape_stations()

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from radio_scraper import scrape_stations

app = FastAPI()

# Allow frontend JS fetches
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (HTML, CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open("static/index.html") as f:
        return f.read()

@app.get("/stations")
async def get_stations():
    try:
        data = await scrape_stations()
        return data
    except Exception as e:
        print("❌ Error in /stations:", e)
        return {"error": str(e)}

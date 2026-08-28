 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from tinyfish import TinyFish
from dotenv import load_dotenv
import os
import json

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = TinyFish(api_key=os.getenv("TINYFISH_API_KEY"))


# ── Option A: Streaming (collect all events, return final output) ──────────────
@app.post("/compare")
def compare_products(product_name: str):
    output_parts = []

    with client.agent.run(
        url=f"https://www.amazon.in/s?k={product_name}",
        goal="Extract first 2 product names and prices in JSON format like [{name, price}]",
    ) as stream:
        for event in stream:
            # Collect the output text from each event
            if hasattr(event, "output") and event.output:
                output_parts.append(event.output)

    full_output = "".join(output_parts)

    # Try to parse as JSON if the model returned valid JSON
    try:
        data = json.loads(full_output)
    except json.JSONDecodeError:
        data = full_output  # Return raw string if not valid JSON

    return {"data": data}


# ── Option B: True SSE streaming response to the client ────────────────────────
@app.post("/compare/stream")
def compare_products_stream(product_name: str):
    def event_generator():
        with client.agent.run(
            url=f"https://www.amazon.in/s?k={product_name}",
            goal="Extract first 2 product names and prices in JSON format like [{name, price}]",
        ) as stream:
            for event in stream:
                yield f"data: {json.dumps({'event': str(event)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")



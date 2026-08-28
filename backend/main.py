from fastapi import FastAPI
from tinyfish import TinyFish
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import json
from groq import Groq
from pydantic import BaseModel


load_dotenv()

app = FastAPI()


print("TinyFish API:", os.getenv("TINYFISH_API_KEY"))
print("Groq API:", os.getenv("GROQ_API_KEY"))

tinyfish_client = TinyFish(api_key=os.getenv("TINYFISH_API_KEY"))
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ProductRequest(BaseModel):
    product_name: str

class Query(BaseModel):
    query: str



@app.get("/ask")
def ask_ai(query: str):
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "user", "content": query}
            ]
        )

        return {"response": response.choices[0].message.content}

    except Exception as e:
        return {"error": str(e)}



def get_ai_advice(product_name, amazon, flipkart):
    try:
        if not amazon and not flipkart:
            return "No product data found. Please try another search."

        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a smart shopping assistant who compares products."
                },
                {
                    "role": "user",
                    "content": f"""
Compare Amazon and Flipkart results for: {product_name}

Amazon: {amazon[:5]}
Flipkart: {flipkart[:5]}

Give short answer:
- Best platform
- Reason
- Best product
"""
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"AI Error: {str(e)}"



def scrape(url, goal):
    raw = None
    
    try:
        with tinyfish_client.agent.stream(url=url, goal=goal) as stream:
            for event in stream:
                print("EVENT:", event)

                if hasattr(event, "result_json") and event.result_json:
                    raw = event.result_json

                elif hasattr(event, "message") and event.message:
                    print("RAW MESSAGE:", event.message)

                    try:
                        cleaned = event.message.strip()
                        raw = json.loads(cleaned)
                    except Exception as e:
                        print("JSON PARSE ERROR:", e)
                        raw = None

    except Exception as e:
        print("SCRAPE ERROR:", e)
        return []

    
    if isinstance(raw, dict):
        return raw.get("products", []) or raw.get("items", []) or raw.get("results", [])

    return []



@app.post("/compare")
def compare_products(req: ProductRequest):
    product_name = req.product_name

    print("Searching for:", product_name)

    
    amazon_data = scrape(
        f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}",
        f"""
Search Amazon India for {product_name}.
Return ONLY JSON:

{{
  "products": [
    {{"name": "...", "price": "..."}}
  ]
}}
"""
    )

    
    flipkart_data = scrape(
        f"https://www.flipkart.com/search?q={product_name.replace(' ', '+')}",
        f"""
Search Flipkart for {product_name}.
Return ONLY JSON:

{{
  "products": [
    {{"name": "...", "price": "..."}}
  ]
}}
"""
    )

    if not amazon_data:
        print("Amazon failed → using fallback")
        amazon_data = [
            {"name": f"{product_name} (Amazon Sample)", "price": "not fetch"},
            {"name": f"{product_name} (Amazon Sample 2)", "price": "not fetch"},
        ]

    if not flipkart_data:
        print("Flipkart failed → using fallback")
        flipkart_data = [
            {"name": f"{product_name} (Flipkart Sample)", "price": "fetch"},
            {"name": f"{product_name} (Flipkart Sample 2)", "price": "fetch"},
        ]

    
    ai_recommendation = get_ai_advice(product_name, amazon_data, flipkart_data)

    return {
        "amazon": amazon_data[:5],
        "flipkart": flipkart_data[:5],
        "ai_recommendation": ai_recommendation
    }







@app.post("/search")
def search_agent(req: Query):
    query = req.query
    raw_data = ""

    try:
        with tinyfish_client.agent.stream(
            url="https://www.google.com",
            goal=f"""
Search Google for: {query}

Extract top 5 results.

Return ONLY:
Title - short description
"""
        ) as stream:
            for event in stream:
                if hasattr(event, "message") and event.message:
                    print("EVENT:", event.message)
                    raw_data += event.message

    except Exception as e:
        return {"error": str(e)}

    
    if not raw_data.strip():
        raw_data = f"""
Top results for {query}:
1. Example result
2. Example result
3. Example result
"""

    
    ai_response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "Summarize clearly in bullet points."
            },
            {
                "role": "user",
                "content": raw_data[:1500]
            }
        ]
    )

    return {
        "result": ai_response.choices[0].message.content
    }
    
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


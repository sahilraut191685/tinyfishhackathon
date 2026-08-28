# Smart Shopper – AI Shopping Assistant
 
An AI-powered shopping assistant that helps users compare products and make smarter purchase decisions, built for the TinyFish Hackathon.
 
## Features
 
- AI-driven product comparison and recommendations
- FastAPI backend for handling requests and processing data
- Simple web frontend for interacting with the assistant
## Tech Stack
 
- **Backend:** Python, FastAPI
- **Frontend:** HTML, CSS, JavaScript
## Project Structure
 
```
tinyfish_hackathon/
├── backend/
│   ├── main.py       # FastAPI app entry point
│   └── tiny.py       # Core logic / AI integration
├── frontend/
│   ├── index.html
│   └── smart_shopper_frontend.html
└── README.md
```
 
## Setup & Installation
 
1. Clone the repository:
```bash
   git clone https://github.com/sahilraut191685/tinyfishhackathon.git
   cd tinyfishhackathon
```
 
2. Create and activate a virtual environment:
```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
```
 
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
 
4. Set up environment variables:
   Create a `.env` file in the `backend/` folder with your required API keys/config.
5. Run the backend server:
```bash
   cd backend
   uvicorn main:app --reload
```
 
6. Open the frontend:
   Open `frontend/index.html` (or `smart_shopper_frontend.html`) in your browser.
## Usage
 
1. Open the frontend in your browser.
2. Enter the product or shopping query you want help with.
3. The AI assistant compares options and returns recommendations.
## Team
 
Built by Sahil Raut for the TinyFish Hackathon.
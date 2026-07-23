# DebateArena

Where ideas clash and knowledge wins.

## Tech Stack

**Frontend:** Next.js 15, React 19, TypeScript, Tailwind CSS, shadcn/ui, Framer Motion, Lucide React  
**Backend:** Python 3.12+, FastAPI, Uvicorn, Pydantic, python-dotenv

## Project Structure

```
DebateArena/
├── frontend/          # Next.js app
├── backend/           # FastAPI server
├── .gitignore
└── README.md
```

## Prerequisites

- Node.js 18+
- Python 3.12+

## Getting Started

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python main.py
```

The backend runs at `http://localhost:8000`.

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend runs at `http://localhost:3000`.

## API Endpoints

| Method | Path      | Description             |
|--------|-----------|-------------------------|
| GET    | `/health` | Health check            |

**GET /health** returns:

```json
{
  "status": "ok",
  "message": "DebateArena Backend Running"
}
```

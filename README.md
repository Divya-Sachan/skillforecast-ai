# SkillForecast AI — Full Ready Website
AI-Based Future Job Skill Demand Prediction System.

## Includes
- React + Vite professional dashboard
- FastAPI backend
- ML skill-demand forecasting with Linear Regression
- Skill trend dashboard
- Personal skill-gap analysis
- Career readiness score
- Personalized learning roadmap
- Job-description skill extraction
- Demo dataset
- No API key required

## Run
### Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

### Frontend (new Terminal)
cd frontend
npm install
npm run dev

Then open the localhost URL shown by Vite.

## Important
The included dataset is demo/synthetic academic data. For a research paper, replace it with a properly licensed public job-posting dataset and report its source.

from pathlib import Path
import re
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.linear_model import LinearRegression

BASE=Path(__file__).resolve().parent.parent
DATA=BASE/'data'/'skill_demand.csv'
app=FastAPI(title='SkillForecast AI API')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_methods=['*'],allow_headers=['*'])

ROLES={
'Software Developer':['Python','Java','React','SQL','Cloud Computing','Docker','Generative AI','Machine Learning'],
'AI/ML Engineer':['Python','Machine Learning','Generative AI','Data Science','Cloud Computing','SQL','Docker'],
'Data Scientist':['Python','Data Science','SQL','Machine Learning','Cloud Computing','Generative AI'],
'Full Stack Developer':['React','Node.js','SQL','Cloud Computing','Docker','Python'],
'Cybersecurity Analyst':['Cybersecurity','Python','Cloud Computing','SQL','Docker']
}
SKILLS=['Python','Java','React','Node.js','Generative AI','Machine Learning','Data Science','Cloud Computing','AWS','Docker','SQL','Cybersecurity','Basic HTML/CSS','FastAPI']

class Gap(BaseModel): target_role:str; skills:list[str]
class Road(BaseModel): target_role:str; skills:list[str]; priority_skills:list[str]=[]
class Job(BaseModel): text:str

def df(): return pd.read_csv(DATA)
def forecast(d,s):
    r=d[d.skill==s].sort_values('year')
    if r.empty:return None
    m=LinearRegression().fit(r[['year']],r.demand_index)
    pred=max(0,min(100,float(m.predict([[r.year.max()+1]])[0])))
    cur=float(r.iloc[-1].demand_index); ch=(pred-cur)/cur*100 if cur else 0
    slope=float(m.coef_[0])
    trend='Fast Rising' if slope>=5 else 'Rising' if slope>=.8 else 'Stable' if slope>-.8 else 'Declining'
    return {'skill':s,'values':r.demand_index.astype(int).tolist(),'current':round(cur,1),'predicted':round(pred,1),'change':round(ch,1),'trend':trend,'category':str(r.iloc[-1].category)}

@app.get('/api/trends')
def trends():
    d=df();return {'trends':[forecast(d,s) for s in d.skill.unique()]}

@app.post('/api/skill-gap')
def gap(x:Gap):
    d=df(); role=ROLES.get(x.target_role,ROLES['Software Developer']); have=set(x.skills);rank=[]
    for s in role:
        if s not in have:
            f=forecast(d,s)
            if f: rank.append((f['predicted'],s,f['trend']))
    rank.sort(reverse=True); miss=[s for _,s,_ in rank]; priority=miss[:5]
    readiness=round(max(35,min(96,100-len(miss)/max(1,len(role))*65)))
    insight=f'{priority[0]} is your highest-priority gap for {x.target_role}.' if priority else 'Your current skills align well with the selected role.'
    return {'target_role':x.target_role,'readiness':readiness,'missing_skills':miss,'priority_skills':priority,'insight':insight}

@app.post('/api/roadmap')
def roadmap(x:Road):
    s=x.priority_skills or ['Python','Machine Learning','Generative AI','Cloud Computing']
    groups=[('01–02','Core foundation',s[:2],'Strengthen fundamentals.'),('03–05','Machine Learning',[z for z in s if z in ['Machine Learning','Data Science','Python']][:2] or s[:1],'Learn model building and evaluation.'),('06–08','Generative AI',[z for z in s if z=='Generative AI'] or ['Generative AI'],'Learn LLM concepts and AI application patterns.'),('09–10','Cloud & deployment',[z for z in s if z in ['Cloud Computing','AWS','Docker']][:2] or ['Cloud Computing'],'Deploy an AI-enabled application.'),('11–12','Portfolio project',['React','FastAPI'],'Build and document one measurable project.')]
    return {'weeks':[{'week':a,'title':b,'skills':c,'goal':d} for a,b,c,d in groups]}

@app.post('/api/analyze-job')
def analyze(x:Job):
    t=x.text.lower();found=[]
    for s in SKILLS:
        if re.search(r'\b'+re.escape(s.lower())+r'\b',t):found.append(s)
    if 'javascript' in t:found.append('JavaScript')
    if 'llm' in t and 'Generative AI' not in found:found.append('Generative AI')
    return {'skills':list(dict.fromkeys(found)),'message':'These skills can be compared with market forecasts to identify learning priorities.' if found else 'No demo-dictionary skills detected. Try a job description containing Python, React, AWS, SQL or Machine Learning.'}

@app.get('/api/health')
def health():return {'status':'healthy'}

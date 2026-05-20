
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
jobs = pd.read_csv('jobs.csv', sep='\t')

print(jobs.columns)  

jobs.columns = jobs.columns.str.strip()

# Remove Serial No column if exists
if 'Serial No' in jobs.columns:
    jobs = jobs.drop('Serial No', axis=1)
    
# Convert skills into vectors
tfidf = TfidfVectorizer()
tfidf_matrix = tfidf.fit_transform(jobs['Skills'])

def recommend_jobs(user_skills):
    user_vector = tfidf.transform([user_skills])
    
    similarity = cosine_similarity(user_vector, tfidf_matrix)
    
    scores = list(enumerate(similarity[0]))
    sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
    
    top_jobs = sorted_scores[:10]
    
    results = []
    for i in top_jobs:
        job = jobs.iloc[i[0]]
        results.append({
            "title": job['Job_Title'],
            "skills": job['Skills'],
            "location": job['Location'],
            "salary": job['Salary'],
            "score": round(i[1]*100, 2)
        })
    
    return results
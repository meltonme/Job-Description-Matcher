from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
import spacy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# Read the index.html file once at startup
with open('index.html', 'r') as file:
    index_html = file.read()

@app.route('/')
def index():
    return render_template_string(index_html)

@app.route('/match', methods=['POST'])
def match():
    job_description = request.form['job_description']
    keywords = request.form['keywords'].split(',')
    resume = request.files['resume']
    filename = secure_filename(resume.filename)
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(resume_path)
    
    match_score, matched_keywords, missing_keywords = match_job_description_to_resume(job_description, keywords, resume_path)
    
    feedback = {
        'match_score': match_score,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords
    }
    
    return jsonify(feedback)

def match_job_description_to_resume(job_description, keywords, resume_path):
    with open(resume_path, 'r') as file:
        resume_content = file.read()
    
    doc_resume = nlp(resume_content)
    matched_keywords = []
    missing_keywords = []

    for keyword in keywords:
        if keyword.lower() in doc_resume.text.lower():
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)
    
    match_score = round((len(matched_keywords) / len(keywords)) * 100) if keywords else 0
    
    return match_score, matched_keywords, missing_keywords

if __name__ == '__main__':
    app.run(debug=True)







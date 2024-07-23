from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import spacy

app = Flask(__name__, template_folder='.')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    match_score = None
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No file part')
            return redirect(request.url)

        job_description = request.form['job_description']
        resume = request.files['resume']

        if resume.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if resume:
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            resume.save(resume_path)
            
            # Extract text from the resume
            resume_text = extract_text_from_pdf(resume_path)
            
            # Calculate the match score
            match_score = match_job_description_to_resume(job_description, resume_text)
    
    return render_template('index.html', match_score=match_score)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def match_job_description_to_resume(job_description, resume_text):
    job_desc_doc = nlp(job_description.lower())
    resume_doc = nlp(resume_text.lower())

    # Extract keywords and filter out stop words
    job_desc_keywords = [token.lemma_ for token in job_desc_doc if token.is_alpha and not token.is_stop]
    resume_keywords = [token.lemma_ for token in resume_doc if token.is_alpha and not token.is_stop]

    # Calculate matching score based on common keywords
    common_keywords = set(job_desc_keywords) & set(resume_keywords)
    score = len(common_keywords) / len(set(job_desc_keywords)) * 100

    return round(score, 2)

if __name__ == '__main__':
    app.run(debug=True)









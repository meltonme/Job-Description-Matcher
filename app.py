from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
import spacy
from PyPDF2 import PdfReader

app = Flask(__name__, template_folder='.')
app.secret_key = 'supersecretkey'  # Required for flashing messages

# Load the trained SpaCy model
nlp = spacy.load("models/custom_ner_model")

@app.route('/', methods=['GET', 'POST'])
def index():
    match_score = None
    matched_keywords = []
    unmatched_keywords = []
    entities = []

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
            # Read file directly into memory
            resume_text = extract_text_from_pdf(resume)
            
            # Calculate the match score and keywords
            match_score, matched_keywords, unmatched_keywords = match_job_description_to_resume(job_description, resume_text)

            # Perform NER prediction
            doc = nlp(resume_text)
            entities = [(ent.text, ent.label_) for ent in doc.ents]

            # Debugging output
            print(f"Job Description: {job_description}")
            print(f"Resume Text: {resume_text}")
            print(f"Match Score: {match_score}")
            print(f"Matched Keywords: {matched_keywords}")
            print(f"Unmatched Keywords: {unmatched_keywords}")
            print(f"Entities: {entities}")

            return render_template('index.html', 
                                   match_score=match_score, 
                                   matched_keywords=matched_keywords, 
                                   unmatched_keywords=unmatched_keywords, 
                                   entities=entities)

    return render_template('index.html', match_score=match_score, matched_keywords=matched_keywords, unmatched_keywords=unmatched_keywords)

def extract_text_from_pdf(resume_file):
    text = ""
    reader = PdfReader(resume_file)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def match_job_description_to_resume(job_description, resume_text):
    job_desc_doc = nlp(job_description.lower())
    resume_doc = nlp(resume_text.lower())

    # Extract keywords and filter out stop words
    job_desc_keywords = [token.lemma_ for token in job_desc_doc if token.is_alpha and not token.is_stop]
    resume_keywords = [token.lemma_ for token in resume_doc if token.is_alpha and not token.is_stop]

    # Debugging output
    print(f"Job Description Keywords: {job_desc_keywords}")
    print(f"Resume Keywords: {resume_keywords}")

    # Calculate matching score
    common_keywords = set(job_desc_keywords) & set(resume_keywords)
    matched_keywords = list(common_keywords)
    unmatched_keywords = list(set(job_desc_keywords) - common_keywords)

    print(f"Common Keywords: {common_keywords}")

    score = len(common_keywords) / len(set(job_desc_keywords)) * 100 if job_desc_keywords else 0

    return round(score, 2), matched_keywords, unmatched_keywords

if __name__ == '__main__':
    app.run(debug=True)






















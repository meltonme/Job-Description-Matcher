from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import fitz  # PyMuPDF
from docx import Document
import spacy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load spaCy model
nlp = spacy.load('en_core_web_md')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/match', methods=['POST'])
def match():
    if 'job_description' not in request.form or 'resume' not in request.files:
        return 'Job description or resume file missing', 400

    job_description = request.form['job_description']
    keywords_input = request.form['keywords']
    resume = request.files['resume']

    if resume.filename == '':
        return 'No selected file', 400

    filename = secure_filename(resume.filename)
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(resume_path)
    
    # Convert user input keywords to a list
    keywords = [keyword.strip() for keyword in keywords_input.split(',')]

    # Use the new matching logic with spaCy
    match_score, feedback = match_job_description_to_resume(job_description, resume_path, keywords)
    
    return jsonify({'Match Score': f'{match_score:.2f}', 'Feedback': feedback})

def match_job_description_to_resume(job_description, resume_path, keywords):
    # Extract text based on file extension
    file_extension = os.path.splitext(resume_path)[1].lower()
    if file_extension == '.pdf':
        resume_content = extract_text_from_pdf(resume_path)
    elif file_extension == '.docx':
        resume_content = extract_text_from_docx(resume_path)
    else:
        with open(resume_path, 'r') as file:
            resume_content = file.read()

    # Process the job description and resume content with spaCy
    job_desc_doc = nlp(job_description)
    resume_doc = nlp(resume_content)

    # Generate feedback based on user-defined keywords
    feedback = generate_feedback(job_desc_doc, resume_doc, keywords)

    # Calculate match score based on the number of matched keywords
    match_score = (len([item for item in feedback if "Matched keyword" in item]) / len(keywords)) * 100

    return match_score, feedback

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in doc:
        text += page.get_text()
    return text

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def generate_feedback(job_desc_doc, resume_doc, keywords):
    feedback = []

    # Extract key phrases and named entities from the job description and resume
    job_keywords = [chunk.text for chunk in job_desc_doc.noun_chunks]
    resume_keywords = [chunk.text for chunk in resume_doc.noun_chunks]

    # Check for user-defined keyword matches
    for keyword in keywords:
        if any(keyword.lower() in job_keyword.lower() for job_keyword in job_keywords):
            if any(keyword.lower() in resume_keyword.lower() for resume_keyword in resume_keywords):
                feedback.append(f'Matched keyword: {keyword}')
            else:
                feedback.append(f'Missing keyword: {keyword}')

    return feedback

if __name__ == '__main__':
    app.run(debug=True)






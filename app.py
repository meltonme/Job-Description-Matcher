from flask import Flask, request, jsonify, render_template_string
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import docx
import spacy

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Load spaCy model for stop word removal
nlp = spacy.load("en_core_web_sm")

# Extract text from PDF and DOCX file types 
def extract_text_from_pdf(pdf_path):
    text = ''
    reader = PdfReader(pdf_path)
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return '\n'.join([para.text for para in doc.paragraphs])

# Remove stop words
def remove_stop_words(text):
    doc = nlp(text)
    return ' '.join([token.text for token in doc if not token.is_stop and not token.is_punct])

@app.route('/')
def index():
    return render_template_string(open('index.html').read())

@app.route('/match', methods=['POST'])
def match():
    job_description = request.form['job_description']
    resume = request.files['resume']
    filename = secure_filename(resume.filename)
    resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    resume.save(resume_path)
    
    # Extract text from resume based on its file type
    if filename.endswith('.pdf'):
        resume_text = extract_text_from_pdf(resume_path)
    elif filename.endswith('.docx'):
        resume_text = extract_text_from_docx(resume_path)
    else:
        return 'Unsupported file format', 400

    # Remove stop words from the job description
    clean_job_description = remove_stop_words(job_description)
    
    # Analyze the cleaned job description against the resume content
    matched_keywords = [word for word in clean_job_description.split() if word.lower() in resume_text.lower()]
    missing_keywords = [word for word in clean_job_description.split() if word.lower() not in resume_text.lower()]
    
    match_score = round((len(matched_keywords) / len(clean_job_description.split())) * 100) if clean_job_description else 0

    # Clean up by deleting the uploaded file after processing
    os.remove(resume_path)
    
    return jsonify({
        'match_score': match_score,
        'matched_keywords': matched_keywords,
        'missing_keywords': missing_keywords
    })

if __name__ == '__main__':
    app.run(debug=True)








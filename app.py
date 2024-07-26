from flask import Flask, request, render_template
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

def extract_text_from_pdf(pdf_path):
    try:
        text = ''
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text += page.extract_text() or ''
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"

def extract_text_from_docx(docx_path):
    try:
        doc = docx.Document(docx_path)
        return '\n'.join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        job_description = request.form.get('job_description')
        keywords = request.form.get('keywords', '').split(',')
        resume = request.files.get('resume')

        if not job_description:
            return render_template('index.html', error='Job description is required')

        if not resume:
            return render_template('index.html', error='Resume file is required')

        filename = secure_filename(resume.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        resume.save(resume_path)

        # Extract text from resume based on its file type
        if filename.endswith('.pdf'):
            resume_text = extract_text_from_pdf(resume_path)
        elif filename.endswith('.docx'):
            resume_text = extract_text_from_docx(resume_path)
        else:
            os.remove(resume_path)
            return render_template('index.html', error='Unsupported file format')

        # Remove stop words from the job description
        doc = nlp(job_description)
        clean_job_description = ' '.join([token.text for token in doc if not token.is_stop and not token.is_punct])

        # Include user-provided keywords and filter by them
        if keywords:
            keywords = [keyword.strip() for keyword in keywords if keyword.strip()]
            clean_job_description = ' '.join([word for word in clean_job_description.split() if word in keywords])

        # Analyze the cleaned job description against the resume content
        matched_keywords = [word for word in clean_job_description.split() if word.lower() in resume_text.lower()]
        missing_keywords = [word for word in clean_job_description.split() if word.lower() not in resume_text.lower()]

        match_score = round((len(matched_keywords) / len(clean_job_description.split())) * 100) if clean_job_description else 0

        # Clean up by deleting the uploaded file after processing
        os.remove(resume_path)

        result = {
            'match_score': match_score,
            'matched_keywords': matched_keywords,
            'missing_keywords': missing_keywords
        }

        return render_template('index.html', result=result)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)






























# Job Description Matcher


This is a Flask application that matches job descriptions against resumes to calculate a match score based on the presence of user provided keywords. 

The application supports PDF and DOCX file formats for resumes.

## Technologies Used 

- **Flask**: A micro web framework for Python, used to handle HTTP requests and serve the application
- **Werkzeug**: A comprehensive WSGI web application library used for file handling.
- **PyPDF2**: A PDF library in Python, used to extract text from PDF files.
- **python-docx**: A library for creating, modifying, and extracting text from Microsoft Word (.docx) files.
- **spaCy**: An open-source software library for advanced natural language processing, used to remove stop words from the job description.

## Methodology

1. **File Upload**: Users can upload their resumes in PDF or DOCX format through a web form.
2. **Text Extraction**: The application extracts text from the uploaded resume file.
3. **Stop Word Removal**: Stop words are removed from the provided job description using the spaCy library.
4. **Keyword Matching**: The application matches keywords from the cleaned job description against the text extracted from the resume.
5. **Score Calculation**: A match score is calculated based on the presence of job description keywords in the resume.
6. **Result Display**: The application returns the match score, matched keywords, and missing keywords as a JSON response.
7. **Custom Keyword Matching**: Users can also provide specific keywords to match against the resume, allowing for flexible and targeted analysis.


## Dependencies

Ensure you have the following dependencies installed:

- Flask
- Werkzeug
- PyPDF2
- python-docx
- spaCy
- en_core_web_sm model for spaCy

You can install the required packages using pip:

```sh
pip install Flask Werkzeug PyPDF2 python-docx spacy
```

```
python -m spacy download en_core_web_sm
```

## Running the Application

Once you have cloned the repository and installed the necessary dependencies, run the Flask application with: 
```
python app.py
```
From there, open your web browser and navigate to the below address to use the application. 
```
http:///127.0.0.7:5000
```

## Usage 

1. Open the application in your browser.
2. Paste the job description and/or specific keywords in the provided text area.
3. Upload your resume in PDF or DOCX format.
4. Click the "Submit" button to get your match score and keyword analysis.

# Training Your Model 

This project includes framework for users to train their own custom named entity recongition (NER) model using SpaCy. The structure for the custom model is shown below: 
```
Job Description Matcher/
│
├── models/
│   └── custom_ner_model/
│       ├── ner/
│       ├── tokenizer/
│       ├── meta.json
│       └── config.cfg
├── training/
│   ├── automated_cleaning.py  # Used to fix any data integrity issues
│   ├── dataintegretycheck.py  # Used to check if the data in the fixed_data.json is correct
│   └── train_model.py         # Script to train the model
```




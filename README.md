# Resume Doctor

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)  
[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)

<img src="https://github.com/vishulearner/resume_doctor/blob/master/Logo/SRA_Logo.png">

## Source

- Extracting user's information from the Resume, I used [PyResparser](https://omkarpathak.in/pyresparser/)
- Extracting Resume PDF into Text, I used [PDFMiner](https://pypi.org/project/pdfminer/).
- For Creating UI, I used [Streamlit](http://streamlit.io/) Library

## Features

- User's & Admin Section
- Extracting User's Info from resume
- Download the Users Data in CSV format
- Analysis of User's Data
- Analysis of User's Data Filtered By Domain
- Resume Score
- Career Recommendations
- Resume writing Tips suggestions
- Courses Recommendations
- Skills Recommendations
- Youtube video recommendations

## Usage

- Clone my repository.
- Open CMD in working directory.
- Run following command.
  ```
  pip install -r requirements.txt
  ```
- `App.py` is the main Python file of Streamlit Web-Application.
- `Courses.py` is the Python file that contains courses and youtube video links.
- Download XAMP or any other control panel, and turn on the Apache & SQL service.
- To run app, write following command in CMD. or use any IDE.
  ```
  streamlit run App.py
  ```
- `Uploaded_Resumes` folder is contaning the user's uploaded resumes.
- `Classifier.py` is the main file which is containing a KNN Algorithm.

## Screenshots

## Admin Side

<img src="https://github.com/vishulearner/resume_doctor/blob/master/Logo/SRA_Logo.png">

## User side

<img src="https://github.com/vishulearner/resume_doctor/blob/master/Logo/SRA_Logo.png">

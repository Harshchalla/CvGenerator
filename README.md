# Cover Letter Generator
# cv.harshchalla.me
This project is a **Flask-based web application** designed to generate **tailored cover letters** based on your resume and a provided job description. The application extracts text from a resume PDF, analyzes the job description, and then uses a **large language model (Meta-Llama-3.1-8B-Instruct-Turbo)** via the **Together API** to create a personalized cover letter. The generated cover letter is saved as a PDF and can be downloaded by the user.

## Features

- **Resume Parsing:** Extracts text from a PDF resume using `PyPDF2`.
- **Job Description Analysis:** Automatically extracts the company name from the job description for personalized salutations.
- **Cover Letter Generation:** Creates a custom cover letter tailored to the job description using information extracted from your resume.
- **PDF Generation:** The cover letter is saved as a PDF using `FPDF`, formatted for easy readability and professionalism.
- **GPT-2 Tokenization:** Ensures token limits are adhered to when sending requests to the Together API by using the `GPT2TokenizerFast`.
- **Together API Integration:** Uses the Together API to access large language models for generating text.
  
## Prerequisites

1. **Python 3.7+**: Make sure you have Python installed on your system.
2. **Together API Key**: You need an API key from [Together](https://www.together.xyz/) to use their language models.
3. **Resume PDF**: Ensure that your resume is available in PDF format, named `resume.pdf`.

## Tech Stack

- **Flask**: Backend framework for serving the web app.
- **PyPDF2**: Library for extracting text from PDF files.
- **FPDF**: Library for generating PDF files.
- **Transformers**: Tokenization and text processing via Hugging Face's `GPT2TokenizerFast`.
- **Together API**: Provides the large language model for generating text.

## Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cover-letter-generator.git
cd cover-letter-generator
```

### 2. Install Dependencies

First, ensure that you have **pip** (Python's package installer) installed, and then run:

```bash
pip install -r requirements.txt
```

**Dependencies:**
- Flask
- PyPDF2
- FPDF
- transformers
- together

### 3. Set Up Together API Key

You need to set your Together API key as an environment variable for authentication. You can do this by adding the following line to your `.bashrc`, `.bash_profile`, or `.zshrc` (depending on your shell), or set it manually in your terminal:

```bash
export TOGETHER_API_KEY="your_api_key_here"
```

### 4. Structure

Make sure your project structure looks like this:

```
cover-letter-generator/
│
├── templates/
│   └── index.html     # Basic HTML form for uploading job description
│
├── static/
│   ├── css/
│   └── fonts/          # Custom fonts like 'Times-Roman' for PDF generation
│
├── resume.pdf          # Your resume in PDF format
├── together.py         # Together API integration code
├── app.py              # Main Flask application
├── README.md           # Project readme
├── requirements.txt    # Python dependencies
```

### 5. Running the Application

Run the Flask application using:

```bash
python app.py
```

By default, Flask will start a local web server on `http://127.0.0.1:5000/`. Open this URL in your browser to access the app.

### 6. Using the Application

1. **Job Description**: Fill in the job description form.
2. **Generate Cover Letter**: Click on the "Generate Cover Letter" button.
3. **Download PDF**: The cover letter will be generated as a PDF, which you can download.

### 7. Custom Fonts for PDF

Make sure that you have custom fonts like **Times-Roman** placed under the `static/fonts/` directory to properly render bullet points and special characters.

Example:

```
pdf.add_font('Times-Roman', '', 'static/fonts/times.ttf', uni=True)
```

## API Overview

### Endpoints

- `/`: The index route renders a form to input the job description.
- `/generate_cover_letter`: This endpoint handles form submission, generates the cover letter using the Together API, and returns the PDF file for download.

### Key Functions

- **`extract_text_from_pdf(pdf_path)`**: Extracts text from the resume PDF.
- **`extract_company_name(job_description)`**: Uses regex to find the company name from the job description.
- **`create_cover_letter_prompt(resume_text, job_description)`**: Builds a prompt for the Together API to generate the cover letter.
- **`save_as_pdf(content, company_name)`**: Saves the generated cover letter content as a PDF file.
  


The cover letter is tailored to each job description, using real data from the user's resume. It follows a professional structure, including bullet points to highlight key skills and experiences relevant to the job.

## Error Handling

- **PDF Parsing Error**: If there's an issue reading the resume, an error message is shown on the frontend.
- **Job Description Missing**: Users will be prompted to provide a job description if left blank.
- **Token Limit Exceeded**: Ensures that the input does not exceed the token limit for Together API calls.

## Future Improvements

- **Multiple Resume Support**: Allow users to upload multiple resumes and select one.
- **Cover Letter Customization**: Add fields for users to input custom details like hiring manager's name or specific job roles.
- **Enhanced Frontend**: Improve the UI/UX for a more user-friendly experience.


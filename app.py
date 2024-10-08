import os
import re
from flask import Flask, render_template, request, send_file
from together import Together
import PyPDF2
from fpdf import FPDF
from transformers import GPT2TokenizerFast

# Initialize tokenizer
tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")

app = Flask(__name__)

# Function to extract text from your resume PDF
def extract_text_from_pdf(pdf):
    try:
        # Check if the input is a FileStorage object or a file path
        if isinstance(pdf, (str, os.PathLike)):
            # It's a file path, open the file normally
            with open(pdf, "rb") as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()
        else:
            # It's a file-like object (FileStorage), read from it directly
            reader = PyPDF2.PdfReader(pdf)
            text = ""
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()

        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""


# Function to extract company name from job description
def extract_company_name(job_description):
    match = re.search(r"\b(?:at|for)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", job_description)
    if match:
        return match.group(1)
    else:
        return None

# Function to create a cover letter prompt
def create_cover_letter_prompt(resume_text, job_description):
    company_name = extract_company_name(job_description)
    
    if company_name:
        header = f"Dear Hiring Manager at {company_name},\n"
    else:
        header = "Dear Hiring Manager,\n"

    footer = "\nSincerely, [NAME_IN_RESUME]]"

    prompt = f"""
You are a professional cover letter writer tasked with generating a tailored cover letter. Use only the information from my resume to craft the cover letter. Do **not fabricate** any experiences, qualifications, or skills. Your goal is to showcase my strengths by using real examples from my resume and relating them to the key requirements of the job description.

**Instructions:**
1. Carefully review the job description and identify the top 3 or 4 most important skills or qualities that the employer is seeking.
2. Analyze my resume to find examples of real experiences that demonstrate I possess these skills. **Do not make up any stories**—only use information from my resume.
3. When matching my experience to the job, create specific examples from my past roles to show how my skills align with the job requirements.
4. Format the body of the cover letter using bullet points to clearly demonstrate how my experience meets each key skill or quality. Each bullet point should reference an actual project or role I’ve undertaken.
3. **When referencing these specific statements from the job description in the cover letter, include the exact phrase or sentence from the job description, and enclose it in double underscores (e.g., __Designs, develops, and .......etc __).**

**Cover Letter Structure:**
- Start with "{header.strip()}" and end with "{footer.strip()}"
- The body should focus exclusively on how my **actual experiences** align with the job's key skills or qualities. For each skill or quality, provide a clear and concrete example from my resume.
- Ensure the cover letter remains concise and professional. There should be no additional commentary or fictional details.

**Resume:**
{resume_text}

**Job Description:**
{job_description}

Please only include the formatted cover letter with no additional text or explanations.
"""

    return prompt


# Function to save the response as a PDF
def save_as_pdf(content, company_name="Company"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(left=7, top=7, right=7)
    pdf.add_font('Times-Roman', '', 'fonts/times.ttf', uni=True)
    pdf.set_font('Times-Roman', '', 12)

    line_height = 5  # Adjusted to make sure each line has space
    content = content.replace('*', '')

    for line in content.split("\n"):
        index = 0
        while index < len(line):
            if line[index:index+2] == '__':
                # Underlined text starts
                index += 2
                end_index = line.find('__', index)
                if end_index == -1:
                    # No closing '__', treat rest of line as underlined
                    underlined_text = line[index:]
                    index = len(line)
                else:
                    underlined_text = line[index:end_index]
                    index = end_index + 2  # Move index past closing '__'
                # Set font to underline
                pdf.set_font('Times-Roman', 'U', 12)
                pdf.write(line_height, underlined_text)
                # Reset font
                pdf.set_font('Times-Roman', '', 12)
            else:
                # Normal text
                next_underline = line.find('__', index)
                if next_underline == -1:
                    text = line[index:]
                    index = len(line)
                else:
                    text = line[index:next_underline]
                    index = next_underline
                pdf.write(line_height, text)
        pdf.ln(line_height)

    # Set file name based on the company name or a default name
    if company_name:
        pdf_name = f"{company_name}_Cover_Letter.pdf"
    else:
        pdf_name = "Cover_Letter.pdf"

    # Save the PDF directly to disk
    pdf.output(pdf_name)

    return pdf_name

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_cover_letter', methods=['POST'])
def generate_cover_letter():
    job_description = request.form.get('job-description')
    resume_file = request.files.get('resume')  # Handle the uploaded resume

    if not job_description:
        return "No job description provided", 400

    if resume_file:
        resume_text = extract_text_from_pdf(resume_file)  # Use uploaded resume
    else:
        resume_text = extract_text_from_pdf("resume.pdf")  # Use default resume.pdf

    if not resume_text:
        return "No resume found", 400

    # Create the cover letter prompt
    prompt = create_cover_letter_prompt(resume_text, job_description)

    # Tokenize the input (prompt) to estimate the token count
    input_token_count = len(tokenizer.encode(prompt))

    # Calculate max_tokens allowed based on input token count
    max_allowed_tokens = 131072  - input_token_count  # Mistral-7B Instruct max tokens


    if max_allowed_tokens <= 0:
        return "Input too large, reduce resume or job description size", 400

    # Limit max_tokens to avoid exceeding token limits
    max_tokens = min(max_allowed_tokens, 131072)
  # Adjust max_tokens if necessary

    # Call the Together API with the generated prompt
    client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))
    response = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",  # Updated model
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,  # Adjusted dynamically
        temperature=0.7,
        top_p=0.7,
        top_k=50,
        repetition_penalty=1,
        stop=["[/INST]", "</s>"],
        stream=False
    )


    # Get the generated cover letter
    cover_letter = response.choices[0].message.content

    # Extract company name for file naming
    company_name = extract_company_name(job_description)

    # Save the cover letter as a PDF
    pdf_file_path = save_as_pdf(cover_letter, company_name)

    # Return the PDF file as a download
    # Clean up the company name to remove newline characters
    if company_name:
         company_name = company_name.replace('\n', '').replace('\r', '').strip()
    else:
        company_name = "Na"
    # Return the PDF file as a download
    return send_file(pdf_file_path, download_name=f"{company_name}_Cover_Letter.pdf", as_attachment=True, mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True)

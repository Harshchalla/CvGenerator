import os
import re
from together import Together
import PyPDF2
from fpdf import FPDF

# Function to extract text from your resume PDF
def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in range(len(reader.pages)):
                text += reader.pages[page].extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""

# Function to extract company name from job description
def extract_company_name(job_description):
    # Try to find a phrase like "at [Company]" or "for [Company]"
    match = re.search(r"\b(?:at|for)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)", job_description)
    if match:
        return match.group(1)
    else:
        return None

# Function to create a cover letter prompt
def create_cover_letter_prompt(resume_text, job_description):
    company_name = extract_company_name(job_description)
    
    # Constructing the cover letter structure
    if company_name:
        header = f"Dear Hiring Manager at {company_name},\n"
    else:
        header = "Dear Hiring Manager,\n"

    footer = "\nThank you,\nHarsh Victor Challa"

    prompt = f"""
    You are an expert cover letter writer. Based on the following resume and job description, write a professional, tailored cover letter:

    RESUME:
    {resume_text}

    JOB DESCRIPTION:
    {job_description}

    Please start the letter with "{header.strip()}" and end it with "{footer.strip()}". The cover letter should highlight relevant skills and experiences from the resume that match the job description. The cover letter should be concise, professional, and ready to submit.
    Do not add text lile "[Company name] or  [Your PhoneNumber] or [Your Email Address]" AND DO not add any other text such as"I hope this cover letter helps you in your job application! Good luck." after the cover letter or  " Sure! Here is a professional, tailored cover letter for the position of E-Commerce Data Analyst at Premier
Staffing Solution:" before the cover ltter

Start the output from "dear" and end with "Sincerely, Harsh Victor Challa"
    """
    return prompt

# Function to get the entire job description in one go
def get_job_description():
    print("Please paste the job description and press Enter when done:")
    return input()

# Function to save the response as a PDF
def save_as_pdf(content, company_name="Company"):
    # Use FPDF to create the PDF
    pdf = FPDF()
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Times", size=12)
    pdf.set_margins(left=7, top=7, right=7)
    # Split content by lines for proper formatting
    lines = content.split("\n")
    
    # Add each line to the PDF
    line_height = 5

    # Add each line to the PDF
    lines = content.split("\n")
    for line in lines:
        pdf.multi_cell(0, line_height, line)
    
    # Set file name
    if company_name:
        pdf_name = f"{company_name}_Cover_Letter.pdf"
    else:
        pdf_name = "Cover_Letter.pdf"

    # Save the PDF
    pdf.output(pdf_name)
    print(f"PDF saved as {pdf_name}")

# Initialize the Together client
client = Together(api_key=os.environ.get('TOGETHER_API_KEY'))

# Extract resume text
resume_text = extract_text_from_pdf("resume.pdf")

# Get job description from user
job_description = get_job_description()

# Ensure both resume and job description exist
if not resume_text:
    print("No resume found, exiting.")
    exit()

if not job_description:
    print("No job description provided, exiting.")
    exit()

# Create the cover letter prompt using the inputted job description
prompt = create_cover_letter_prompt(resume_text, job_description)

# Call the Together API with the generated prompt
response = client.chat.completions.create(
    model="meta-llama/Llama-2-13b-chat-hf",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=1536,
    temperature=0.7,
    top_p=0.7,
    top_k=50,
    repetition_penalty=1,
    stop=["[/INST]", "</s>"],
    stream=False  # Set to True if you want to stream the response
)

# Get the generated cover letter
cover_letter = response.choices[0].message.content

# Extract company name for file naming
company_name = extract_company_name(job_description)

# Save the cover letter as a PDF
save_as_pdf(cover_letter, company_name)

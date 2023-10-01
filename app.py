import streamlit as st
import openai as ai
from PyPDF2 import PdfReader
from webscrapper import scrapper



ai.api_key = st.secrets["openai_key"]

st.markdown("""
# 📝 Cold E-mail Generator based on LLM

Generate a customized e-mail to showcase your interests to a Recruiter based on your resume and given job description
1. Upload your resume or copy your resume or experiences
2. Enter/Paste URL of the company or company description
3. Enter/Paste a relevant job description or URL for the same
4. Input/Paste some other relevant company or job description
"""
)

# Option to upload or copy paste resume
res_format = st.radio(
    "Do you want to upload or paste your resume/key experience",
    ('Upload', 'Paste'))

if res_format == 'Upload':
    # upload_resume
    res_file = st.file_uploader('📁 Upload your resume in pdf format')
    if res_file:
        pdf_reader = PdfReader(res_file)

        # Collect text from pdf
        res_text = ""
        for page in pdf_reader.pages:
            res_text += page.extract_text()
else:
    # use the pasted contents instead
    res_text = st.text_input('Paste resume elements')

with st.form('input_form'):
    # other inputs
    user_name = st.text_input('Your name')
    manager = st.text_input('Hiring manager')
    role = st.text_input('Job title/role')
    company = st.text_input('Company name')
    mission = st.text_input(f"Enter company URL {1} or Paste about the Company")
    job_desc = st.text_input(f"Enter Job Description URL {2} or Paste the relevant JD")
    referral = st.text_input('How did you find out about this opportunity?')
    ai_temp = st.number_input('AI Temperature (0.0-1.0) Input how creative the API can be',value=.90)

    # submit button
    submitted = st.form_submit_button("Generate an Email Draft")





    # if the form is submitted run the openai completion
    if submitted:
        # note that the ChatCompletion is used as it was found to be more effective to produce good results
        # using just Completion often resulted in exceeding token limits
        # according to https://platform.openai.com/docs/models/gpt-3-5
        # Our most capable and cost effective model in the GPT-3.5 family is gpt-3.5-turbo which has been optimized for chat
        # but works well for traditional completions tasks as well.

        mission_desc = scrapper(mission)
        job_desc_det = scrapper(job_desc)

        completion = ai.ChatCompletion.create(
            # model="gpt-3.5-turbo-16k",
            model="gpt-3.5-turbo",
            temperature=ai_temp,

            messages=[
                {"role": "user",
                 "content": f"You will need to generate an email to a recruiter on what's interest you to join this company based on specific resume,a job description and company's mission"},
                {"role": "user", "content": f"Extracted about the company, mission, goals and objective: {mission_desc}"},
                {"role": "user", "content": f"My resume text: {res_text}"},
                {"role": "user", "content": f"Extracted ob description, Roles & Responsibilities and skills: {job_desc_det}"},
                {"role": "user", "content": f"The candidate's name to include on the email: {user_name}"},
                {"role": "user", "content": f"The job title/role : {role}"},
                {"role": "user", "content": f"The hiring manager is: {manager}"},
                {"role": "user", "content": f"How you heard about the opportunity: {referral}"},
                {"role": "user", "content": f"The company to which you are generating the cover letter for: {company}"},
                {"role": "user", "content": f"The cover letter should have three content paragraphs"},
                {"role": "user", "content": f""" 
            In the first 100 words focus on the following: you will convey who you are, what position you are interested in,
             how your skills matches with the company's mission, and where you heard
            about it, and summarize what you have to offer based on the above resume
            """},
                {"role": "user", "content": f""" 
            In the last 100 words focus on why the candidate is a great fit drawing parallels between the experience 
            included in the resume and the qualifications on the job description. also Restate your interest in the organization 
            and/or job and summarize what you have to offer and thank the reader for their time and consideration.
            """},
                {"role": "user", "content": f""" 
            note that contact information may be found in the included resume text and use and/or summarize specific resume context for the email
                """},
                {"role": "user", "content": f"Use {user_name} as the candidate"},

                {"role": "user",
                 "content": f"Generate a specific email based on the above in not more than 195 words and focus on polite manner. Generate the response and include appropriate spacing between the paragraph text"}
            ]
        )

        response_out = completion['choices'][0]['message']['content']
        st.write(response_out)

        # include an option to download a txt file
        #st.download_button('Download the Email Draft', response_out)
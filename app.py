import streamlit as st
import os
import fitz  
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

def ui():
    st.markdown(
        '<link href="https://cdnjs.cloudflare.com/ajax/libs/mdbootstrap/4.19.1/css/mdb.min.css" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" '
        'integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" '
        'crossorigin="anonymous">',
        unsafe_allow_html=True,
    )
    
    hide_streamlit_style = """
                <style>
                    header{visibility:hidden;}
                    .main {
                        margin-top: -20px;
                        padding-top:10px;
                    }
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
                    .reportview-container {
                        padding-top: 0;
                    }
                    .loan-summary {
                        background-color: white;
                        padding: 20px;
                        color:black;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);
                    }
                    .loan-summary h1 {
                        color: #4267B2;
                        font-size: 24px;
                        margin-bottom: 20px;
                    }
                    .loan-summary h2 {
                        color: #4267B2;
                        font-size: 18px;
                        margin-top: 15px;
                        margin-bottom: 10px;
                    }
                    .loan-summary hr {
                        margin: 15px 0;
                    }
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.markdown(
        """
        <nav class="navbar fixed-top navbar-expand-lg navbar-dark" style="background-color: #4267B2;">
        <a class="navbar-brand" href="#"  target="_blank">Loan Document Analyzer</a>  
        </nav>
    """,
        unsafe_allow_html=True,
    )

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_multiple_pdfs(uploaded_files):
    """Extract text from multiple uploaded PDFs using PyMuPDF."""
    extracted_texts = []
    for uploaded_file in uploaded_files:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        extracted_texts.append(text)
    return " ".join(extracted_texts)

def get_completion(prompt):
    """Get completion from OpenAI API."""
    try:
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a loan officer creating a concise, professional summary of loan application documents. Focus on key information and present it in a clear, structured format."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while communicating with OpenAI: {str(e)}")
        return None

def generate_loan_summary(extracted_text):
    """Generate a comprehensive but concise loan summary."""
    prompt = f"""
    Create a concise, one to two page summary of this loan application, if the content is english get output in english and if content is german, get it in german. Structure the summary as follows:

    1. APPLICANT OVERVIEW
    - Full name, contact details (format appropriately)
    - Brief employment status
    - Key financial indicators (income, major assets)

    2. LOAN REQUEST
    - Amount requested
    - Purpose of loan
    - Proposed terms (if specified)

    3. DOCUMENTATION VERIFICATION
    - List provided documents
    - Note any missing critical documents
    - Confirm validity of identity documents

    4. FINANCIAL ASSESSMENT
    - Monthly income
    - Debt-to-income ratio
    - Major assets and liabilities
    - Credit score/history summary

    5. RISK ANALYSIS
    - Key strengths of application
    - Potential concerns
    - Mitigating factors

    6. RECOMMENDATION
    - Clear approval/denial recommendation
    - If approved, suggested terms
    - If denied, primary reasons

    Format the summary in a professional, easy-to-read manner. Be concise but thorough.
    Use bullet points where appropriate for readability.

    Documents text:
    {extracted_text}
    """
    return get_completion(prompt)

def display_summary(summary):
    """Display the loan summary in a nicely formatted way."""
    st.markdown("""
    <div class="loan-summary">
        <h1>Loan Application Summary</h1>
        {summary}
    </div>
    """.format(summary=summary.replace('\n', '<br>')), unsafe_allow_html=True)

def main():
    ui()
    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    
    st.markdown("### Required Documentation")
    st.info("""
    Please provide the following documents:
    1. Completed application form
    2. Proof of identity (two forms required)
    3. Income verification documents
    """)

    uploaded_files = st.file_uploader("Upload loan application documents (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        with st.spinner("Processing Documents..."):
            extracted_text = extract_text_from_multiple_pdfs(uploaded_files)
        st.success(f"Successfully processed {len(uploaded_files)} documents")

        if st.button('Generate Loan Summary'):
            with st.spinner("Analyzing documents and generating summary..."):
                loan_summary = generate_loan_summary(extracted_text)
                if loan_summary:
                    display_summary(loan_summary)
                    
                    # Add download button for the summary
                    st.download_button(
                        label="Download Summary",
                        data=loan_summary,
                        file_name="loan_summary.txt",
                        mime="text/plain"
                    )
    
    else:
        st.write("Please upload the required loan application documents to begin analysis.")

if __name__ == "__main__":
    main()

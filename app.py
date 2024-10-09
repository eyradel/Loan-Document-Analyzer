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
    st.markdown("", unsafe_allow_html=True)

    hide_streamlit_style = """
                <style>
                    header{visibility:hidden;}
                    .main {
                        margin-top: -20px;
                        padding-top:10px;
                    }
                    #MainMenu {visibility: hidden;}
                    footer {visibility: hidden;}
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

ui()


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
                {"role": "system", "content": "You are a loan officer analyzing documents."},
                {"role": "user", "content": prompt}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        st.error(f"An error occurred while communicating with OpenAI: {str(e)}")
        return None

def process_loan_summary(extracted_text):
    """Generate a loan summary using OpenAI."""
    prompt = f"""
    Based on the following loan application documents, provide a concise summary of:
    1. Applicant's personal information
    2. Loan amount requested
    3. Purpose of the loan
    4. Financial information (income, assets, debts)
    5. Credit history highlights
    6. Any red flags or concerns

    Documents text:
    {extracted_text}
    """
    return get_completion(prompt)

def process_detailed_analysis(extracted_text):
    """Generate a detailed loan analysis using OpenAI."""
    prompt = f"""
    Provide a detailed analysis of these loan application documents with the following structure:

    1. APPLICANT PROFILE
    - Name and contact information
    - Employment history
    - Current income and employment status

    2. LOAN DETAILS
    - Requested amount
    - Purpose of loan
    - Proposed terms

    3. FINANCIAL ASSESSMENT
    - Income analysis
    - Debt-to-income ratio
    - Asset verification
    - Liabilities

    4. CREDIT ANALYSIS
    - Credit score
    - Payment history
    - Outstanding debts
    - Previous loans

    5. RISK ASSESSMENT
    - Identify potential risks
    - Mitigating factors
    - Recommendation

    Documents text:
    {extracted_text}
    """
    return get_completion(prompt)

def main():
    """Main function to run the Streamlit app."""

    
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
        return
    

    uploaded_files = st.file_uploader("Upload loan application documents (PDF)", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:

        with st.spinner("Extracting Text from Documents..."):
            extracted_text = extract_text_from_multiple_pdfs(uploaded_files)
        st.success("Text Extracted Successfully")
        
        
        

        if st.button('Analyze Loan Documents'):
            with st.expander("Summary"):
                with st.spinner("Generating Summary..."):
                    summary = process_loan_summary(extracted_text)
                    if summary:
                        st.subheader("Loan Summary")
                        st.write(summary)
            
            with st.expander("Detailed Analysis"):
                with st.spinner("Performing Detailed Analysis..."):
                    detailed_analysis = process_detailed_analysis(extracted_text)
                    if detailed_analysis:
                        st.subheader("Detailed Loan Analysis")
                        st.write(detailed_analysis)
    
    else:
        st.write("Please upload loan application documents to begin analysis.")

if __name__ == "__main__":
    main()
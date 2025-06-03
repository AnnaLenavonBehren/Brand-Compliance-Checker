import streamlit as st
import requests
import json

# Initialize session state flags
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = None
if "context" not in st.session_state:
    st.session_state.context = ""

# Set tab and title
st.set_page_config(page_title="Check Brand Compliance", page_icon=":sunglasses:")
st.title("Check Brand Compliance :sunglasses:")

# Add option to add pdf
pdf_doc = st.file_uploader("Upload brand compliance PDF", type="pdf")

# Add upload button
if pdf_doc:
    if st.button("Upload PDF", key="upload_pdf_button"):
        # Add spinner to tell user to wait
        with st.spinner("Processing"):
            # Get pdf
            files = {"file": (pdf_doc.name, pdf_doc.getvalue(), "application/pdf")}
            try:
                response = requests.post("http://backend:8000/upload/", files=files)
                response.raise_for_status()

                context = response.json()
                context_str = json.dumps(context)
                
                # Save context in session_state to be able to reuse it later
                st.session_state.context = context_str  
                st.session_state.pdf_uploaded = True

                st.success("PDF processed successfully!")

            except requests.RequestException as e:
                st.error(f"❌ Upload failed: {e}")

            

elif pdf_doc is None and st.session_state.pdf_uploaded is not None:
    # File was removed, clear stored file
    st.session_state.pdf_uploaded = None
    st.session_state.context = ""

if st.session_state.pdf_uploaded:
    image = st.file_uploader("Upload your asset", type=["png", "jpg"])

    if image and st.button("Upload image", key="upload_image_button"):
        with st.spinner("Analyzing"):
            image_files = {"file": (image.name, image.getvalue(), image.type)}

            try:
                context = st.session_state.context

                data = {'context': context}

                # st.title("Context")
                # st.write(context)

                response = requests.post('http://backend:8000/check_image/', files=image_files, data=data)

                response.raise_for_status()
                result_json = response.json()
                st.success("✅ Upload successful!")
                
                
                total_value = sum(int(result["requirement"]) for result in result_json["results"])

                # Summarizing results
                st.title("Requirement Summary")

                # Show total value first
                st.write("### Total Requirement Value")
                st.success(f"Total Value: {total_value} of 4 categories fulfill the requirements.")

                # Expandable section for detailed results
                with st.expander("Show Detailed Results"):
                    for result in result_json["results"]:
                        st.write(f"**Category**: {result['category']}")
                        st.write(f"Requirement: {'Fulfilled.' if int(result['requirement']) == 1 else 'Not fulfilled.'}")
                        st.write(f"Reason: {result['reason']}")
                        st.write("")

            except requests.RequestException as e:
                st.error(f"❌ Upload failed: {e}")
# main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from data_processing import extract_pdf_text
from llm import summarize_compliance_information, BrandComplianceLLM
from typing import List, Any
import json
from data_models import MultiResultModel, ComplianceInformationModel

app = FastAPI()

# Allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Process PDF: Extract raw text data and summarize it LLM-based
@app.post("/upload/", response_model=ComplianceInformationModel)
async def upload_pdf(file: UploadFile = File(...)):

    text_unstructured = await extract_pdf_text(file)

    context = await summarize_compliance_information(text_unstructured)
    print(context)

    return context

# Analyze whether a provided image fulfills a company's style guide (context)
@app.post("/check_image/", response_model=MultiResultModel)
async def check_brand_compliance(file: UploadFile = File(...), context: str = Form(...)):

    parsed_context = json.loads(context)
    llm = BrandComplianceLLM(parsed_context, "gpt-4o-mini")

    result = await llm.check_brand_compliance(file)
    
    return result
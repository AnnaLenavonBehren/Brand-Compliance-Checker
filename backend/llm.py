import ollama
from data_models import ComplianceInformationModel, MultiResultModel
from langchain_openai import ChatOpenAI
import base64
from data_processing import load_prompt
from langchain_core.prompts import ChatPromptTemplate 
from pydantic import ValidationError
from dotenv import load_dotenv
from fastapi import FastAPI
import os

load_dotenv()

#ollama_url = "http://ollama:11434"
#client = ollama.Client(host=ollama_url)
ollama.base_url = os.getenv("OLLAMA_HOST", "http://localhost:11434")

class BrandComplianceLLM:     

    def __init__(self, context : str, model_type = "gpt-4o-mini"):
         
        # Brand compliance context information
        self.context = context

        # Initialize model
        self.llm = ChatOpenAI(model = model_type)

        # Define prompt
        self.prompt = ChatPromptTemplate(
        [
            {
                "role": "system",
                "content": """
                    You receive context information about a company's style guide and should interpret whether a given image fulfills those requirements.
                    {question}
                    Return 0, if it's not fulfilled and 1, if it is. You always have to return either one of them. If you don't know, then guess.

                    Please provide a brief reason for your decision, include specifics that link to the style guide.

                    Requirements / Style Guide: 
                    {style_guide}
                """
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source_type": "base64",
                        "mime_type": "{image_mime_type}",
                        "data": "{image_base64}",
                    },
                ],
            },
        ]
        )

        # Define langchain chain for inference
        self.chain = self.prompt | self.llm


    # Check whether a given image fulfills brand style requirements provided in self.context 
    async def check_brand_compliance(self, uploaded_file):
        image_mime_type = uploaded_file.content_type

        # Read bytes from the uploaded file
        file_bytes = await uploaded_file.read()
    
        # Encode to base64
        image_base64 = base64.b64encode(file_bytes).decode("utf-8")

        # Image color check
        path_color = "prompts/image_color_scheme.txt"
        question_color = load_prompt(path_color)
        response_colors = self.invoke(image_base64, image_mime_type, question_color)
        
        # Font check
        path_font = "prompts/font_prompt.txt"
        question_font = load_prompt(path_font)
        response_font = self.invoke(image_base64, image_mime_type, question_font)

        # Logo color check
        path_logo_color_scheme= "prompts/logo_color_scheme.txt"
        question_logo_color_scheme = load_prompt(path_logo_color_scheme)
        response_logo_color_scheme = self.invoke(image_base64, image_mime_type, question_logo_color_scheme)

        # Logo safe zone check
        path_safe_zone = "prompts/logo_safe_zone.txt"
        question_safe_zone = load_prompt(path_safe_zone)
        response_safe_zone = self.invoke(image_base64, image_mime_type, question_safe_zone)


        result = self.summarize_results(response_colors, response_font, response_logo_color_scheme, response_safe_zone)

        return result

        
    # Summarize the results from the four individual analyses and put them into a predefined MultiResultModel structure
    def summarize_results(self, response_color, response_font, response_logo_colors, response_safe_zone):
        prompt_result = f"""
            You are providing the final summary of four image analyses. You are given four messages.
            Summarize them into 
                - Category: Each category's title exactly as given, do not leave categories out, each of the four should receive an entry!
                - Requirement: Number 1 or 0, according to whether the requirements are accepted (1) or not (0), do not change the provided results
                - Reason: A good and detailed reason for your decision
    
            Message 1: Overall color palette
            {response_color}

            Message 2: Font style
            {response_font}

            Message 3: Logo colors
            {response_logo_colors}

            Message 4: Logo safe zone
            {response_safe_zone}

        """

        # Call model (mistral) to summarize and structure the individual analyses
        response = ollama.chat(model="mistral", messages = [
            {
                "role" : "user",
                "content" : prompt_result
            },
        ],format=MultiResultModel.model_json_schema())
    
        result = response["message"]["content"]

        # Guarantee that the infromation is of type MultiResultModel (four ResultModels)
        try:
            parsed = MultiResultModel.parse_raw(result)
            return parsed
        except ValidationError as e:
            raise ValueError(f"Model parsing failed: {e}")
    

    

    

    # Call model with image and context information (from constructor)
    def invoke(self, image_base64 : base64, image_mime_type : str, question : str):
        return self.chain.invoke({
            "image_base64": image_base64, 
            "image_mime_type": image_mime_type,
            "question" : question,
            "style_guide" : self.context}).text()
        

# Summarize raw and unstructured text extracted from a pdf into structured information     
async def summarize_compliance_information(text : str) -> str:
        prompt_summarize = f"""
            You are receiving the unstructured text of a brand compliance information sheet and should extract information about company name, logo colors, font styles, logo safe zone and entire color palette for the entire image from it.
            The company name usually appears more often than once in the entire text.
            Do not exclude information you do not deem necessary if they are connected to the question. Include them all, but structure them.

            Styleguide: 
            {text}
        """
        
        # Call model (mistral) for unstructured text summarization
        response = ollama.chat(model="mistral", messages = [
            {
                "role" : "user",
                "content" : prompt_summarize
            },
        ],format=ComplianceInformationModel.model_json_schema())

        context = response["message"]["content"]


        # Guarantee that the infromation is of type ComplianceInformationModel
        try:
            parsed = ComplianceInformationModel.parse_raw(context)
            return parsed
        except ValidationError as e:
            raise ValueError(f"Model parsing failed: {e}")

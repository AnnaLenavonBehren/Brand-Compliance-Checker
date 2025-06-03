# Brand Compliance Checker

This application checks whether images align with a brand's style guide.  
It uses Ollama Mistral and OpenAI GPT-4o-mini to extract key information from your company's style guide and a provided image.

## Configuration
1. Clone the git repository
   ```
   https://github.com/AnnaLenavonBehren/Brand-Compliance-Checker
   ```

2. Change to the project repository
    ```
    cd Brand-Compliance-Checker
    ```

3. Add a file `.env` with your OpenAI API Key
   ```
   export OPENAI_API_KEY="YOUR API KEY HERE"
   ```

4. Build docker container
   ```
   docker compose up --build
   ```

5. Visit [http://localhost:8501/](http://localhost:8501/) to open the Web UI  


**Notes:**  
- Ensure that you have a running installation of [Docker](https://docs.docker.com/get-started/get-docker/) and [Ollama](https://ollama.com/download) on your PC.
- The docker-compose assumes GPU usage, adjust if necessary.  


## Usage

The application should look like this:
![image](https://github.com/user-attachments/assets/b3403c2f-2073-4eee-be6f-429a96b8c290)

You can then upload a PDF imcluding your company's style guide and the tool extracts the following key information:
- Font style
- Logo safe zone
- Logo colours
- Colour palette (overall image)  

Depending on your local machine this may take a while.  

Once the information are extracted, you can upload an image (png or jpg):  

![image](https://github.com/user-attachments/assets/d75cf8d7-d632-461f-a450-586427a8d3ca)

It then outputs a score from 1 to 4, one for each category. A drop down menu shows why or why not certain points got assigned.

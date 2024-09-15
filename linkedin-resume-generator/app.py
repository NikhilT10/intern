from flask import Flask, request, send_file, render_template
from PyPDF2 import PdfReader
import openai
from io import BytesIO

# Initialize the Flask application
app = Flask(__name__)

# Route to serve the HTML form
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle file upload and resume generation
@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        file = request.files['file']
        api_key = request.form['apiKey']

        if not file or not api_key:
            return {"error": "File or API key is missing."}, 400

        # Extract text from the PDF
        pdf_reader = PdfReader(file)
        extracted_text = ''
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()

        # Set up OpenAI API key
        openai.api_key = api_key

        # Use `gpt-3.5-turbo` model
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # Updated model
            prompt=f"Convert the following LinkedIn profile information into a professional HTML resume:\n\n{extracted_text}",
            max_tokens=2000,
            temperature=0.5
        )

        # Extract the generated HTML content
        generated_html = response.choices[0].text.strip()

        # Save the HTML to a file
        html_file = BytesIO()
        html_file.write(generated_html.encode('utf-8'))
        html_file.seek(0)

        # Return the HTML file as a download
        return send_file(
            html_file,
            as_attachment=True,
            download_name='resume.html',
            mimetype='text/html'
        )
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)

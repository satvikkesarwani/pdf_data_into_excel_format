from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import os
import json
import pdfplumber
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai
import io
import uuid

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Flask Config
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
app.config['UPLOAD_FOLDER'] = '/tmp/pdf_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

MODEL = "gemini-2.5-pro"

# ==================== PDF EXTRACTION FUNCTIONS ====================

def extract_text_from_pdf(path):
    """Extracts full text to preserve document-wide context."""
    full_text = ""
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                full_text += (page.extract_text() or "") + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return ""
    return full_text

def build_generic_logic_prompt(document_text):
    return f"""
You are an expert Data Structuring Engine. Convert the unstructured text below into a structured JSON dataset.

### INPUT TEXT:
{document_text}

### GENERIC EXTRACTION RULES (Strictly Follow):

1. **Disambiguate Timelines (Logic):** - Analyze dates to distinguish between "First", "Previous", and "Current" roles.
   - **Naming Convention:** Use verbose, descriptive keys. 
     - BAD: "Salary", "Job Title".
     - GOOD: "Salary of first professional role", "Current Designation", "Joining Date of previous organization".

2. **Atomic Data Splitting:**
   - Split Names -> "First Name", "Last Name".
   - Split Locations -> "City", "State".
   - Split Money -> "Value" (Integer only), "Currency" (ISO code).

3. **List Handling (Numbering):**
   - For recurring items (Certifications, Projects), number them explicitly.
   - Format Keys as: "Certifications 1", "Certifications 2".
   - Combine the Name, Year, and Score into the Value/Comments for that number.

4. **Data Normalization:**
   - Dates: YYYY-MM-DD (ISO format).
   - Numbers: Integers only (no commas).
   - Text: Preserve original wording in "Comments".

### OUTPUT FORMAT:
Return a single JSON object with this exact structure:
{{
  "entries": [
    {{ "key": "Field Name", "value": "Extracted Data", "comments": "Verbatim source sentence" }}
  ]
}}
"""

def process_pdf_with_gemini(pdf_path):
    """Process PDF and extract structured data using Gemini."""
    full_text = extract_text_from_pdf(pdf_path)
    if not full_text:
        raise ValueError("Failed to extract text from PDF")

    model = genai.GenerativeModel(MODEL)
    prompt = build_generic_logic_prompt(full_text)
    
    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "temperature": 0.1
        }
    )
    
    parsed_data = json.loads(response.text)
    return parsed_data

def create_excel_from_data(parsed_data):
    """Convert parsed JSON data to Excel file."""
    if "entries" not in parsed_data:
        raise ValueError("Invalid JSON structure: missing 'entries' key")
    
    excel_rows = []
    for i, entry in enumerate(parsed_data["entries"], start=1):
        excel_rows.append({
            "#": i,
            "Key": entry.get("key"),
            "Value": entry.get("value"),
            "Comments": entry.get("comments")
        })
    
    df = pd.DataFrame(excel_rows)
    
    # Write to BytesIO for in-memory file
    output = io.BytesIO()
    df.to_excel(output, index=False, sheet_name='Extracted Data')
    output.seek(0)
    return output

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    html = render_template_string(HTML_TEMPLATE)
    return html

@app.route('/upload', methods=['POST'])
def upload_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({'error': 'Only PDF files are supported'}), 400
        
        # Save uploaded file
        filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process PDF with Gemini
        parsed_data = process_pdf_with_gemini(filepath)
        
        # Create Excel file
        excel_file = create_excel_from_data(parsed_data)
        
        # Clean up uploaded PDF
        os.remove(filepath)
        
        # Return Excel file
        return send_file(
            excel_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='extracted_data.xlsx'
        )
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# ==================== HTML/CSS/JS TEMPLATE ====================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Data Extractor - AI Powered</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1a3e 50%, #0f0f2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
            overflow: hidden;
            position: relative;
        }

        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(circle at 20% 50%, rgba(138, 43, 226, 0.1) 0%, transparent 50%),
                        radial-gradient(circle at 80% 80%, rgba(72, 219, 251, 0.1) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }

        .container {
            width: 100%;
            max-width: 500px;
            z-index: 1;
            position: relative;
        }

        .card {
            background: rgba(255, 255, 255, 0.07);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.6s ease-out;
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            color: #ffffff;
            font-size: 28px;
            margin-bottom: 10px;
            text-align: center;
            background: linear-gradient(135deg, #48dbfb, #a82cff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .subtitle {
            color: rgba(255, 255, 255, 0.6);
            text-align: center;
            margin-bottom: 40px;
            font-size: 14px;
        }

        .upload-section {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }

        .upload-section.hidden {
            display: none;
        }

        .dropzone {
            border: 2px dashed rgba(72, 219, 251, 0.5);
            border-radius: 15px;
            padding: 40px 20px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            background: rgba(72, 219, 251, 0.05);
        }

        .dropzone:hover {
            border-color: rgba(72, 219, 251, 0.8);
            background: rgba(72, 219, 251, 0.1);
            transform: scale(1.02);
        }

        .dropzone.dragover {
            background: rgba(72, 219, 251, 0.15);
            border-color: rgba(72, 219, 251, 1);
            box-shadow: 0 0 20px rgba(72, 219, 251, 0.3);
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 15px;
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }

        .upload-text {
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            margin-bottom: 5px;
        }

        .upload-subtext {
            color: rgba(255, 255, 255, 0.5);
            font-size: 12px;
        }

        input[type="file"] {
            display: none;
        }

        .processing-section {
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 30px;
            animation: fadeIn 0.4s ease-out;
        }

        .processing-section.active {
            display: flex;
        }

        @keyframes fadeIn {
            from {
                opacity: 0;
            }
            to {
                opacity: 1;
            }
        }

        .radar-scanner {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 2px solid rgba(72, 219, 251, 0.3);
            position: relative;
            overflow: hidden;
            box-shadow: 0 0 30px rgba(72, 219, 251, 0.2);
        }

        .radar-circle-1 {
            position: absolute;
            width: 100%;
            height: 100%;
            border: 1px solid rgba(72, 219, 251, 0.2);
            border-radius: 50%;
            animation: expandPulse 3s infinite;
        }

        .radar-circle-2 {
            position: absolute;
            width: 80%;
            height: 80%;
            border: 1px solid rgba(168, 44, 255, 0.2);
            border-radius: 50%;
            top: 10%;
            left: 10%;
            animation: expandPulse 3s infinite 1s;
        }

        .radar-circle-3 {
            position: absolute;
            width: 60%;
            height: 60%;
            border: 1px solid rgba(72, 219, 251, 0.2);
            border-radius: 50%;
            top: 20%;
            left: 20%;
            animation: expandPulse 3s infinite 2s;
        }

        .radar-sweep {
            position: absolute;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(72, 219, 251, 0.5), transparent);
            animation: sweep 2s infinite linear;
        }

        @keyframes expandPulse {
            0% {
                transform: scale(1);
                opacity: 1;
            }
            100% {
                transform: scale(1.3);
                opacity: 0;
            }
        }

        @keyframes sweep {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }

        .processing-text {
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            text-align: center;
            animation: pulse-text 1.5s ease-in-out infinite;
        }

        @keyframes pulse-text {
            0%, 100% { opacity: 0.8; }
            50% { opacity: 1; }
        }

        .download-section {
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            animation: slideUp 0.5s ease-out;
        }

        .download-section.active {
            display: flex;
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .success-icon {
            font-size: 80px;
            animation: popIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }

        @keyframes popIn {
            0% {
                transform: scale(0);
            }
            50% {
                transform: scale(1.1);
            }
            100% {
                transform: scale(1);
            }
        }

        .success-text {
            color: rgba(255, 255, 255, 0.8);
            font-size: 16px;
            text-align: center;
        }

        .download-btn {
            background: linear-gradient(135deg, #22c55e, #16a34a);
            color: white;
            border: none;
            padding: 18px 50px;
            font-size: 16px;
            font-weight: 600;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 30px rgba(34, 197, 94, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .download-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(34, 197, 94, 0.5);
        }

        .download-btn:active {
            transform: translateY(-1px);
        }

        .error-section {
            display: none;
            flex-direction: column;
            align-items: center;
            gap: 20px;
            animation: fadeIn 0.4s ease-out;
        }

        .error-section.active {
            display: flex;
        }

        .error-icon {
            font-size: 60px;
        }

        .error-text {
            color: #ff6b6b;
            font-size: 16px;
            text-align: center;
        }

        .retry-btn {
            background: rgba(255, 255, 255, 0.1);
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 12px 30px;
            font-size: 14px;
            border-radius: 50px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .retry-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            border-color: rgba(255, 255, 255, 0.5);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>📊 PDF Data Extractor</h1>
            <p class="subtitle">AI-powered data extraction & structuring</p>

            <!-- Upload Section -->
            <div class="upload-section" id="uploadSection">
                <div class="dropzone" id="dropzone">
                    <div class="upload-icon">📄</div>
                    <p class="upload-text">Drag & drop your PDF here</p>
                    <p class="upload-subtext">or click to browse</p>
                </div>
                <input type="file" id="fileInput" accept=".pdf">
            </div>

            <!-- Processing Section -->
            <div class="processing-section" id="processingSection">
                <div class="radar-scanner">
                    <div class="radar-circle-1"></div>
                    <div class="radar-circle-2"></div>
                    <div class="radar-circle-3"></div>
                    <div class="radar-sweep"></div>
                </div>
                <p class="processing-text">🤖 AI Extracting Data...</p>
            </div>

            <!-- Download Section -->
            <div class="download-section" id="downloadSection">
                <div class="success-icon">✅</div>
                <p class="success-text">Data extraction complete!</p>
                <button class="download-btn" id="downloadBtn">⬇️ Download Excel</button>
            </div>

            <!-- Error Section -->
            <div class="error-section" id="errorSection">
                <div class="error-icon">⚠️</div>
                <p class="error-text" id="errorText">An error occurred</p>
                <button class="retry-btn" id="retryBtn">Try Again</button>
            </div>
        </div>
    </div>

    <script>
        const dropzone = document.getElementById('dropzone');
        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');
        const processingSection = document.getElementById('processingSection');
        const downloadSection = document.getElementById('downloadSection');
        const errorSection = document.getElementById('errorSection');
        const downloadBtn = document.getElementById('downloadBtn');
        const retryBtn = document.getElementById('retryBtn');
        const errorText = document.getElementById('errorText');

        let excelBlob = null;

        // Dropzone interactions
        dropzone.addEventListener('click', () => fileInput.click());

        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFile(files[0]);
            }
        });

        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFile(e.target.files[0]);
            }
        });

        function handleFile(file) {
            if (!file.name.toLowerCase().endsWith('.pdf')) {
                showError('Please upload a PDF file');
                return;
            }

            uploadFile(file);
        }

        async function uploadFile(file) {
            uploadSection.classList.add('hidden');
            processingSection.classList.add('active');
            errorSection.classList.remove('active');

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const error = await response.json();
                    throw new Error(error.error || 'Upload failed');
                }

                excelBlob = await response.blob();
                showDownload();
            } catch (error) {
                showError(error.message);
            }
        }

        function showDownload() {
            processingSection.classList.remove('active');
            downloadSection.classList.add('active');
        }

        function showError(message) {
            processingSection.classList.remove('active');
            errorText.textContent = message;
            errorSection.classList.add('active');
        }

        downloadBtn.addEventListener('click', () => {
            if (excelBlob) {
                const url = URL.createObjectURL(excelBlob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'extracted_data.xlsx';
                a.click();
                URL.revokeObjectURL(url);
            }
        });

        retryBtn.addEventListener('click', () => {
            errorSection.classList.remove('active');
            uploadSection.classList.remove('hidden');
            fileInput.value = '';
            excelBlob = null;
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5000)
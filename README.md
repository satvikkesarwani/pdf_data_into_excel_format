# PDF Data Extractor - AI Powered

A modern, glassmorphic web application that uses **Google Gemini AI** to intelligently extract, structure, and export data from PDF documents into organized Excel files.

## Features

- Drag & Drop Interface - Intuitive PDF upload with visual feedback
- AI-Powered Extraction - Uses Google Gemini to intelligently parse unstructured data
- Smart Data Structuring - Automatically disambiguates timelines, splits atomic data, and normalizes formats
- Modern UI - Dark-mode glassmorphic design with smooth animations
- Radar Scanner Animation - Futuristic processing indicator with pulsing effects
- One-Click Excel Export - Structured data ready for analysis
- Error Handling - Comprehensive validation and user-friendly error messages
- Real-Time Feedback - Responsive design with instant visual updates

## Tech Stack

- **Backend:** Flask, Python 3.8+
- **AI Engine:** Google Generative AI (Gemini 2.5 Pro)
- **PDF Processing:** pdfplumber
- **Data Export:** pandas, openpyxl
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **HTTP Server:** Werkzeug

## Prerequisites

- Python 3.8 or higher
- Google Gemini API Key
- pip (Python package manager)
- Modern web browser

## Installation

### 1. Clone or Download the Project

```bash
cd pdf-data-extractor
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate on Windows:
```bash
venv\Scripts\activate
```

Activate on macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**How to get your Gemini API Key:**

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Get API Key"
3. Create a new API key
4. Copy and paste into your `.env` file

**Important:** Never commit `.env` to version control. Add it to `.gitignore`.

### 5. Run the Application

```bash
python app.py
```

Open your browser at: `http://localhost:5000`

## Usage Guide

### Upload a PDF

1. Open `http://localhost:5000` in your browser
2. Drag and drop a PDF file onto the upload area, or click to browse
3. The app validates that it's a PDF file

### Wait for Processing

Once uploaded, you will see:

- A beautiful radar scanner animation
- Status text: "AI Extracting Data..."
- Processing happens in the background using Gemini AI

### Download Results

When processing completes:

1. A green "Download Excel" button appears
2. Click the button to download your structured data
3. The file is named `extracted_data.xlsx`

### Review Your Data

Open the Excel file in Excel, Google Sheets, or any spreadsheet application.

Data is organized in columns:

- **#** - Row number
- **Key** - Descriptive field name
- **Value** - Extracted and normalized data
- **Comments** - Original text from PDF

## Data Extraction Logic

The application uses intelligent AI rules to structure PDF data automatically.

### Timeline Disambiguation

The AI distinguishes between different temporal contexts:

- First role/experience
- Previous role/experience
- Current role/experience

### Atomic Data Splitting

Complex data is split into discrete fields:

- Names → First Name, Last Name
- Locations → City, State
- Money → Value (Integer), Currency (ISO Code)

### List Numbering

Recurring items are automatically indexed:

```
Certifications 1 → "AWS Solutions Architect, 2022"
Certifications 2 → "Google Cloud Professional, 2023"
Projects 1 → "E-commerce Platform, React, 2023"
```

### Format Normalization

All data is standardized:

- Dates: YYYY-MM-DD (ISO 8601)
- Numbers: Integers only (no commas)
- Currency: ISO 4217 code (USD, EUR, INR)
- Text: Original wording preserved

## API Endpoints

### GET `/`

Returns the HTML user interface.

### POST `/upload`

Uploads and processes a PDF file.

**Content-Type:** `multipart/form-data`

**Parameters:**

- `file` (required) - PDF file to process

**Success Response (200):**

Returns an Excel file for download

**Error Response (400/500):**

```json
{
  "error": "Error message describing the issue"
}
```

**Example Errors:**

```json
{
  "error": "No file provided"
}
```

```json
{
  "error": "Only PDF files are supported"
}
```

```json
{
  "error": "Failed to extract text from PDF"
}
```

## Configuration

Edit these values in `app.py` to customize the application:

```python
# Maximum file upload size (default: 50MB)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# Temporary upload folder
app.config['UPLOAD_FOLDER'] = '/tmp/pdf_uploads'

# Google Gemini model version
MODEL = "gemini-2.5-pro"

# Server settings
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

## Styling and Customization

The frontend uses a glassmorphic dark-mode design with the following colors:

**Color Scheme:**

- Primary Gradient: Cyan (#48dbfb) to Purple (#a82cff)
- Success Green: #22c55e
- Error Red: #ff6b6b
- Dark Background: #0a0e27 to #1a1a3e

**Animations:**

- Slide-in card entrance (0.6s)
- Floating upload icon (3s)
- Radar scanner pulses (3s)
- Pulsing processing text (1.5s)
- Pop-in success checkmark (0.6s)

To customize colors, edit the `HTML_TEMPLATE` CSS section in `app.py`.

## Troubleshooting

### "GEMINI_API_KEY not found"

Cause: Environment variable not configured

Solution:

1. Create `.env` file in project root
2. Add: `GEMINI_API_KEY=your_key_here`
3. Restart Flask application
4. Verify file exists with `ls -la .env` (macOS/Linux)

### "Only PDF files are supported"

Cause: Uploaded file is not a valid PDF

Solution:

- Verify the file is a real PDF
- Try opening it in Adobe Reader
- Try a different PDF file

### "Failed to extract text from PDF"

Cause: PDF is image-based or corrupted

Solution:

- Ensure PDF contains selectable text (not scanned images)
- Try OCR conversion if you have an image-based PDF
- Test with a different PDF file

### "Port 5000 already in use"

Cause: Another application is using port 5000

Solution - Use a different port:

```python
app.run(debug=True, port=5001)
```

Solution - Kill the process (macOS/Linux):

```bash
lsof -i :5000
kill -9 <PID>
```

Solution - Kill the process (Windows):

```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### "ImportError: No module named 'flask'"

Cause: Dependencies not installed

Solution:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Install all requirements
pip install -r requirements.txt

# Verify installation
pip list | grep Flask
```

### "Connection refused at localhost:5000"

Cause: Flask server not running

Solution:

1. Ensure Flask app is running: `python app.py`
2. Check console for error messages
3. Verify port 5000 is not blocked by firewall
4. Try `http://127.0.0.1:5000` instead of `http://localhost:5000`

## Performance Tips

- Maximum supported file size: 50MB
- Processing time depends on document complexity (typically 5-30 seconds)
- Large PDFs may take longer

**Development Mode:**

```python
app.run(debug=True)  # Auto-reloads on code changes
```

**Production Mode:**

```python
app.run(debug=False)
```

**Increase Upload Limit:**

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

## Deployment

### Local Development

```bash
python app.py
```

Open: `http://localhost:5000`

### Production with Gunicorn

```bash
# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run with custom timeout
gunicorn -w 4 -b 0.0.0.0:5000 --timeout 120 app:app
```

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libpoppler-cpp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--timeout", "120", "app:app"]
```

Build and run:

```bash
docker build -t pdf-extractor .
docker run -e GEMINI_API_KEY="your_key_here" -p 5000:5000 pdf-extractor
```

## Security Best Practices

**Environment Variables:**

```bash
echo ".env" >> .gitignore
```

**API Key Protection:**

- Store API keys in environment variables only
- Never hardcode keys in source files
- Use different API keys for development and production
- Regularly rotate API keys

**File Upload Security:**

- Files are validated before processing
- Uploaded PDFs are stored in temporary directory
- Files are automatically deleted after processing
- File sizes are limited to prevent abuse

**Production Checklist:**

- Set `debug=False` in production
- Use HTTPS/SSL certificates
- Configure CORS if needed
- Implement rate limiting
- Set up logging and monitoring
- Use environment variables for all secrets
- Keep dependencies updated

## Project Structure

```
pdf-data-extractor/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
└── /tmp/pdf_uploads/
```

## Future Enhancements

- Batch processing for multiple PDFs
- Custom extraction templates
- Data validation and verification UI
- Export to multiple formats (CSV, JSON, SQL)
- User authentication and project management
- API rate limiting and usage analytics
- OCR support for image-based PDFs
- Advanced data mapping and transformation
- Webhook integration for automation
- REST API for programmatic access

## License

This project is open source and available for personal and commercial use.

## Support and Resources

- [Google AI Studio](https://aistudio.google.com)
- [Gemini API Documentation](https://ai.google.dev)
- [Flask Documentation](https://flask.palletsprojects.com)
- [pdfplumber GitHub](https://github.com/jsvine/pdfplumber)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

Made with ❤️ using Flask, Gemini AI, and Glassmorphism Design

Python 3.8+ | MIT License | Last Updated 2024

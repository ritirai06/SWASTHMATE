# MedCo Analyzer 🩺

**MedCo Analyzer** is a secure and intelligent medical report analysis system that helps patients, doctors, and healthcare professionals extract actionable insights from medical reports. It leverages **OCR**, **NLP**, and **AI chat assistants** to provide clear, understandable medical information along with personalized recommendations.

This system is designed to be **secure**, **scalable**, and **easy to use**, with all API keys protected via environment variables.

---

## 🚀 Features

* **Medical Report Upload:** Accepts PDFs, images (`png`, `jpg`, `jpeg`, `tiff`) up to 16MB.
* **OCR Integration:** Uses **Azure Form Recognizer** to extract text from scanned medical reports.
* **Medical NLP Analysis:** Extracts diseases, findings, measurements, and patient information using a custom **NLP engine**.
* **AI Recommendations:** Provides personalized suggestions for symptoms using a recommendation engine.
* **AI Q&A Chatbot:** Uses **Google Gemini** and **Cohere** APIs to answer medical questions in English or Hindi with structured, emoji-rich responses.
* **Frontend Dashboard:** Clean interface for uploading reports, viewing results, and interacting with the AI assistant.
* **Secure API Keys:** All API keys (Azure, Cohere, Gemini, AWS) are loaded securely from `.env`.

---

## 📁 Supported File Types

* PDF (`.pdf`)
* PNG (`.png`)
* JPEG (`.jpg`, `.jpeg`)
* TIFF (`.tiff`)

---

## 🛠️ Technology Stack

* **Backend:** Flask, Python 3.11
* **OCR:** Azure Form Recognizer
* **NLP & AI:** Custom `MedicalNLP`, AWS NLP, Google Gemini API, Cohere API
* **Frontend:** HTML, CSS, JavaScript
* **Database / Storage:** Local JSON results storage (can be extended to MongoDB)
* **Security:** Environment variables for all API keys

---

## ⚙️ Installation

1. **Clone the repository**

```bash
git clone https://github.com/your-username/medco-analyzer.git
cd medco-analyzer
```

2. **Create a virtual environment**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

* Windows:

```bash
venv\Scripts\activate
```

* Linux / Mac:

```bash
source venv/bin/activate
```

4. **Install dependencies**

```bash
pip install -r requirements.txt
```

5. **Create a `.env` file** in the root directory with your API keys:

```env
AZURE_ENDPOINT=your_azure_endpoint
AZURE_KEY=your_azure_key
COHERE_API_KEY=your_cohere_api_key
GEMINI_API_KEY=your_gemini_api_key
AWS_ACCESS_KEY=your_aws_access_key
AWS_SECRET_KEY=your_aws_secret_key
```

6. **Run the Flask app**

```bash
python app1.py
```

7. Open your browser at:

```
http://127.0.0.1:5000/
```

---

## 📝 Usage

* **Upload a report:** Navigate to the upload page and upload your medical report.
* **View analysis:** Get extracted text, detected diseases, measurements, and recommendations.
* **Ask AI:** Use the chatbot to ask questions about conditions, treatments, or medical advice.

---

## 🔐 Security Notes

* API keys are **never hard-coded** in the source code.
* Keys are loaded securely using the `.env` file.
* For production deployment, use server-side environment variables and secure storage.

---

## 📂 Folder Structure

```
medco-analyzer/
├─ app1.py                # Main Flask application
├─ nlpengine.py           # NLP processing module
├─ nlp.py                 # Custom MedicalNLP class
├─ recom_engine.py        # Recommendations engine
├─ uploads/               # Uploaded files & results
├─ templates/             # HTML templates
├─ static/
│  ├─ css/
│  └─ js/
├─ requirements.txt       # Python dependencies
└─ .env                   # API keys (not committed to GitHub)
```

---

## 🤖 AI & NLP Features

* Extract diseases, symptoms, and test measurements.
* Generate structured recommendations based on detected conditions.
* AI assistant answers in **English** or **Hindi**, including:

  * Overview
  * Causes
  * Symptoms
  * Treatment
  * When to see a doctor

---

## ⚡ Future Improvements

* Integration with a database (MongoDB/PostgreSQL) for persistent storage.
* User authentication for personalized medical dashboards.
* Multi-language support beyond English and Hindi.
* Mobile-friendly frontend design.

---

## 📞 Contact

For support or inquiries:
**Email:** ritirai0612@gmail.com


---

## 📄 License

This project is licensed under the **MIT License**.


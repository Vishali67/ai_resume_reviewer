import os
import fitz  # PyMuPDF
from flask import Flask, render_template, request
import openai

# Initialize Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

# Helper function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Route for main page
@app.route("/", methods=["GET", "POST"])
def index():
    feedback = None

    if request.method == "POST":
        api_key = request.form.get("api_key")
        if not api_key:
            return render_template("index.html", feedback="Please provide your OpenAI API key.")

        if "resume" not in request.files:
            return render_template("index.html", feedback="No file uploaded")

        file = request.files["resume"]

        if file.filename == "":
            return render_template("index.html", feedback="No selected file")

        if file and file.filename.endswith(".pdf"):
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(file_path)

            resume_text = extract_text_from_pdf(file_path)

            prompt = (
                "You are an expert career coach and resume reviewer. "
                "Review this resume and provide:\n"
                "- Strengths\n"
                "- Weaknesses\n"
                "- Suggestions for improvement\n"
                "- Skills to add\n\n"
                f"Resume:\n{resume_text}"
            )

            try:
                client = openai.OpenAI(api_key=api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful and professional resume reviewer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    temperature=0.7
                )
                feedback = response.choices[0].message.content
            except Exception as e:
                feedback = f"Error: {e}"

    return render_template("index.html", feedback=feedback)

# Run the app
if __name__ == "__main__":
    if not os.path.exists("uploads"):
        os.makedirs("uploads")
    app.run(debug=True)

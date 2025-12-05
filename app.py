from flask import Flask, render_template, request, send_file
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import nltk
from reportlab.pdfgen import canvas

# NLTK required data
nltk.download("punkt")
nltk.download("punkt_tab")

app = Flask(__name__)

# Store latest summary
last_summary_sentences = []
last_summary_type = ""


def generate_summary(text, sentence_count=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LexRankSummarizer()
    summary_sentences = summarizer(parser.document, sentence_count)
    return [str(s) for s in summary_sentences]


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/summarize', methods=['POST'])
def summarize():
    global last_summary_sentences, last_summary_type

    text = request.form.get("text")
    sentences_count = int(request.form.get("sentences"))
    summary_type = request.form.get("summary_type")

    # Generate list of summary sentences
    sentences = generate_summary(text, sentences_count)

    last_summary_sentences = sentences
    last_summary_type = summary_type

    # HTML formatting for web output
    if summary_type == "paragraph":
        final_summary = " ".join(sentences)

    elif summary_type == "points":
        final_summary = "<ul>" + "".join([f"<li>{s}</li>" for s in sentences]) + "</ul>"

    else:  # "sentences"
        final_summary = "<br>".join(sentences)

    return render_template(
        'result.html',
        summary=final_summary,
        summary_type=summary_type
    )


@app.route('/download_summary')
def download_summary():
    global last_summary_sentences, last_summary_type

    pdf_path = "summary.pdf"
    c = canvas.Canvas(pdf_path)
    c.setFont("Times-Roman", 12)

    y = 800  # start writing from top

    # MATCH PDF FORMAT WITH USER SELECTION
    if last_summary_type == "paragraph":
        paragraph = " ".join(last_summary_sentences)
        c.drawString(50, y, paragraph)

    elif last_summary_type == "points":
        for line in last_summary_sentences:
            c.drawString(50, y, "• " + line)  # bullet format
            y -= 20

    else:  # "sentences"
        for line in last_summary_sentences:
            c.drawString(50, y, line)  # each sentence on new line
            y -= 20

    c.save()
    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)

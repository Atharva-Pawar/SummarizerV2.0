from flask import Flask, render_template, request, jsonify
from txtai.pipeline import Summary
from PyPDF2 import PdfReader  # Add this line
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
import os
import json
import re

app = Flask(__name__)

# Utility Functions


def text_summary(text, maxlength=None):
    summary = Summary()
    result = summary(text)
    return result


def extract_text_from_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PdfReader(f)
            text = ""
            for page_number in range(len(pdf_reader.pages)):
                text += pdf_reader.pages[page_number].extract_text()
        return text
    except PyPDF2.errors.EmptyFileError:
        return None


def download_youtube_video(video_url):
    yt = YouTube(video_url)
    video_stream = yt.streams.filter(file_extension="mp4").first()

    # Sanitize the title to remove invalid characters
    title = re.sub(r'[<>:"/\\|?*]', '', yt.title)

    video_path = os.path.join("static/videos", f"{title}.mp4")
    video_stream.download(output_path="static/videos", filename=title)
    return video_path


def extract_transcript(video_url, language="en"):
    try:
        video_id = None
        if "v=" in video_url:
            video_id = video_url.split("v=")[1].split("&")[0]
        elif "youtu.be" in video_url:
            video_id = video_url.split("/")[-1]

        if video_id:
            transcript = YouTubeTranscriptApi.get_transcript(
                video_id, languages=[language])
            text = " ".join([entry['text'] for entry in transcript])
            return text
        else:
            return None
    except Exception as e:
        return None

# Flask Routes


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/summarize_text', methods=['GET', 'POST'])
def summarize_text():
    if request.method == 'POST':
        input_text = request.form['input_text']
        result = text_summary(input_text)
        return jsonify({'result': result})
    return render_template('text-summary.html')


@app.route('/summarize_document', methods=['GET', 'POST'])
def summarize_document():
    if request.method == 'POST':
        try:
            input_file = request.files['input_file']
            file_path = 'static/uploaded_docs/doc_file.pdf'
            input_file.save(file_path)

            extracted_text = extract_text_from_pdf(file_path)

            if extracted_text is None:
                return jsonify({'error': 'Empty or invalid PDF file.'}), 400

            doc_summary = text_summary(extracted_text)
            return jsonify({'extracted_text': extracted_text, 'doc_summary': doc_summary})

        except Exception as e:
            # Return the exception message as an error
            return jsonify({'error': str(e)}), 500

    return render_template('doc-summary.html')


@app.route('/summarize_youtube', methods=['GET', 'POST'])
def summarize_youtube():
    if request.method == 'POST':
        try:
            # Get JSON data from the request
            data = json.loads(request.data)

            # Extract the required information from the JSON data
            video_url = data.get('video_url', '')
            language = data.get('language', 'en')

            # Your existing code for processing YouTube videos
            video_path = download_youtube_video(video_url)
            transcript = extract_transcript(video_url, language)

            if transcript:
                video_summary = text_summary(transcript)
                return jsonify({'result': video_summary})
            else:
                return jsonify({'error': 'Failed to fetch transcript. Please check the video URL.'}), 400

        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid JSON data'}), 400

    return render_template('yt-summary.html')


if __name__ == '__main__':
    app.run(debug=True)

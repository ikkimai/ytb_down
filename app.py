import os
from flask import Flask, render_template, request, jsonify, redirect
from downloader_engine import resolve_media

app = Flask(__name__)
app.secret_key = 'chave_secreta_universal_downloader'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_type = request.form.get('format', 'video')

    if not url:
        return jsonify({'success': False, 'error': 'Por favor, forneça o link do vídeo.'})

    try:
        media_data = resolve_media(url.strip(), format_type=format_type)
        return jsonify(media_data)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/stream')
def stream():
    media_url = request.args.get('url')
    if not media_url:
        return "URL inválida", 400
    return redirect(media_url, code=302)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)

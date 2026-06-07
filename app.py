import os
import glob
from flask import Flask, render_template, request, send_file, jsonify
import yt_dlp

app = Flask(__name__)
app.secret_key = 'chave_secreta_para_flash_messages'

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_type = request.form.get('format', 'video')
    
    if not url:
        return jsonify({'success': False, 'error': 'URL não fornecida.'})
        
    try:
        # Limpar arquivos antigos da pasta downloads para não acumular
        for f in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, f)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception:
                pass

        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
            'restrictfilenames': True,
            'noplaylist': True,
        }
        
        if format_type == 'audio':
            ydl_opts.update({
                'format': 'bestaudio/best',
            })
        else:
            ydl_opts.update({
                'format': 'best',
            })
            
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if not os.path.exists(filename):
                base, _ = os.path.splitext(filename)
                possiveis_arquivos = glob.glob(base + '.*')
                if possiveis_arquivos:
                    filename = possiveis_arquivos[0]
                    
            basename = os.path.basename(filename)
            title = info.get('title', 'Video')
            
            quality_info = "Desconhecida"
            if format_type == 'video':
                width = info.get('width')
                height = info.get('height')
                if width and height:
                    quality_info = f"{width}x{height} (Resolução)"
                else:
                    quality_info = info.get('resolution', 'Máxima disponível')
            else:
                abr = info.get('abr')
                if abr:
                    quality_info = f"{int(abr)} kbps (Taxa de bits)"
                else:
                    quality_info = "Melhor áudio disponível"

        return jsonify({
            'success': True,
            'filename': basename,
            'title': title,
            'quality': quality_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

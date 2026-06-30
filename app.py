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

        if 'instagram.com' in url:
            # Integração com RapidAPI para Instagram
            import urllib.parse
            import requests
            import re
            
            api_key = 'cabf0a23f0mshc6ba466efaeb4b7p133ac0jsn3e3a9c0f2c4b'
            encoded_url = urllib.parse.quote(url)
            headers = {
                'x-rapidapi-host': 'instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com',
                'x-rapidapi-key': api_key
            }
            
            res = requests.get(f'https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi?url={encoded_url}', headers=headers)
            try:
                data = res.json()
            except Exception:
                return jsonify({'success': False, 'error': 'Erro ao se comunicar com a API do Instagram.'})
                
            if data.get('error'):
                return jsonify({'success': False, 'error': data.get('message', 'Erro na API do Instagram.')})
                
            title = data.get('caption', 'instagram_video')
            # Limpar título para não dar erro no nome do arquivo
            if not title:
                title = 'instagram_video'
            title = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
                
            download_url = data.get('download_url')
            if not download_url:
                return jsonify({'success': False, 'error': 'Nenhum vídeo encontrado pela API.'})
                
            extension = 'mp4'
            quality_info = 'Máxima via API'
            
            final_filename = f"{title}.{extension}"
            filepath = os.path.join(DOWNLOAD_DIR, final_filename)
            
            # Fazer o download do arquivo
            r_file = requests.get(download_url, stream=True)
            with open(filepath, 'wb') as f:
                for chunk in r_file.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            final_title = title.replace('_', ' ')
            
        else:
            # yt-dlp para YouTube, TikTok e todos os outros
            ydl_opts = {
                'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                'restrictfilenames': True,
                'noplaylist': True,
            }
            
            cookie_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
            if os.path.exists(cookie_file):
                ydl_opts['cookiefile'] = cookie_file
            
            if format_type == 'audio':
                ydl_opts.update({'format': 'bestaudio[ext=m4a]/bestaudio/best'})
            else:
                ydl_opts.update({'format': 'best[ext=mp4]/best'})
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                if not os.path.exists(filename):
                    base, _ = os.path.splitext(filename)
                    possiveis_arquivos = glob.glob(base + '.*')
                    if possiveis_arquivos:
                        filename = possiveis_arquivos[0]
                        
                final_filename = os.path.basename(filename)
                final_title = info.get('title', 'Video')
                
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
            'filename': final_filename,
            'title': final_title,
            'quality': quality_info
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/files/<path:filename>')
def serve_file(filename):
    return send_file(os.path.join(DOWNLOAD_DIR, filename), as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

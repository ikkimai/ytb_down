import os
import re

def resolve_youtube(url, format_type='video'):
    """
    Extrai o link direto de reprodução/download do YouTube utilizando
    pytubefix (cliente Android/iOS nativo) com fallback para yt-dlp.
    Bypassa o desafio de bot em datacenters (como Vercel/AWS).
    """
    # Limpar parâmetros extras da URL como &list= para evitar erro de playlist
    clean_url = url
    v_match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11})', url)
    if v_match:
        video_id = v_match.group(1)
        clean_url = f"https://www.youtube.com/watch?v={video_id}"

    # Método 1: pytubefix com clientes móveis (ANDROID, IOS, MWEB)
    # Este método não sofre o bloqueio de 'Sign in to confirm you're not a bot'
    for client_name in ['ANDROID', 'IOS', 'MWEB']:
        try:
            from pytubefix import YouTube
            yt = YouTube(clean_url, client=client_name)
            
            title = yt.title or "YouTube_Video"
            thumbnail = yt.thumbnail_url
            duration = f"{yt.length // 60}:{yt.length % 60:02d}" if yt.length else "Vídeo"
            
            if format_type == 'audio':
                stream = yt.streams.get_audio_only()
                if stream and stream.url:
                    return {
                        'success': True,
                        'title': title,
                        'download_url': stream.url,
                        'thumbnail': thumbnail,
                        'duration': duration,
                        'quality': f"{stream.abr or '128kbps'} (Áudio M4A)",
                        'extension': 'm4a',
                        'direct': True,
                        'source': f'YouTube ({client_name})'
                    }
            else:
                stream = yt.streams.get_highest_resolution()
                if stream and stream.url:
                    return {
                        'success': True,
                        'title': title,
                        'download_url': stream.url,
                        'thumbnail': thumbnail,
                        'duration': duration,
                        'quality': f"{stream.resolution or '720p'} (Vídeo + Áudio)",
                        'extension': 'mp4',
                        'direct': True,
                        'source': f'YouTube ({client_name})'
                    }
        except Exception:
            continue

    # Método 2: Fallback para yt-dlp
    import yt_dlp
    cookie_file = None
    if os.environ.get('YOUTUBE_COOKIES'):
        cookie_path = '/tmp/cookies.txt' if os.environ.get('VERCEL') else os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')
        with open(cookie_path, 'w', encoding='utf-8') as f:
            f.write(os.environ['YOUTUBE_COOKIES'])
        cookie_file = cookie_path
    elif os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')):
        cookie_file = os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')

    ydl_opts = {
        'skip_download': True,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web']
            }
        }
    }
    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(clean_url, download=False)
        title = info.get('title', 'Video_YouTube')
        thumbnail = info.get('thumbnail')
        duration = info.get('duration_string') or f"{info.get('duration', 0)}s"
        formats = info.get('formats', [])
        
        selected_url = None
        quality = 'Padrão'
        extension = 'mp4'

        if format_type == 'audio':
            audio_formats = [
                f for f in formats 
                if f.get('acodec') and f.get('acodec') != 'none' 
                and f.get('vcodec') == 'none'
                and f.get('ext') not in ['mhtml']
                and f.get('url') and 'http' in f.get('url')
            ]
            if audio_formats:
                m4a_formats = [f for f in audio_formats if f.get('ext') == 'm4a']
                chosen = m4a_formats[-1] if m4a_formats else audio_formats[-1]
                selected_url = chosen.get('url')
                extension = chosen.get('ext', 'm4a')
                abr = chosen.get('abr')
                quality = f"{int(abr)} kbps (Áudio)" if abr else "Melhor Áudio"
            else:
                f_with_audio = [
                    f for f in formats 
                    if f.get('acodec') and f.get('acodec') != 'none' 
                    and f.get('ext') not in ['mhtml']
                    and f.get('url') and 'http' in f.get('url')
                ]
                if f_with_audio:
                    chosen = f_with_audio[0]
                    selected_url = chosen.get('url')
                    extension = chosen.get('ext', 'mp4')
                    quality = "Áudio Original (AAC/MP4)"
        else:
            progressive = [
                f for f in formats 
                if f.get('vcodec') and f.get('vcodec') != 'none' 
                and f.get('acodec') and f.get('acodec') != 'none' 
                and f.get('ext') not in ['mhtml']
                and f.get('url') and 'http' in f.get('url')
            ]
            if progressive:
                chosen = progressive[-1]
                selected_url = chosen.get('url')
                extension = chosen.get('ext', 'mp4')
                res = chosen.get('resolution') or f"{chosen.get('height', '360')}p"
                quality = f"{res} (Vídeo + Áudio)"
            else:
                any_video = [
                    f for f in formats 
                    if f.get('url') and 'http' in f.get('url') 
                    and f.get('ext') not in ['mhtml']
                ]
                if any_video:
                    chosen = any_video[-1]
                    selected_url = chosen.get('url')
                    extension = chosen.get('ext', 'mp4')
                    quality = chosen.get('resolution', 'Padrão')

        if not selected_url:
            raise Exception("Não foi possível extrair um link de streaming válido para este conteúdo.")

        return {
            'success': True,
            'title': title,
            'download_url': selected_url,
            'thumbnail': thumbnail,
            'duration': duration,
            'quality': quality,
            'extension': extension,
            'direct': True,
            'source': 'YouTube (yt-dlp)'
        }

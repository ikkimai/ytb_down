import re
import urllib.parse
import requests

def resolve_instagram(url, format_type='video'):
    """
    Resolve links do Instagram utilizando múltiplos provedores gratuitos:
    1. Instaloader (raspagem direta sem chaves, ilimitada)
    2. RapidAPI (provedor de backup com a chave do usuário)
    """
    errors = []

    # Extrair shortcode do Instagram
    shortcode_match = re.search(r'(?:reel|p|tv)/([A-Za-z0-9_-]+)', url)
    shortcode = shortcode_match.group(1) if shortcode_match else None

    # Provedor 1: Instaloader (Nativo, direto do CDN da Meta)
    if shortcode:
        try:
            import instaloader
            L = instaloader.Instaloader(
                quiet=True,
                download_pictures=False,
                download_videos=False,
                download_video_thumbnails=False,
                save_metadata=False,
                compress_json=False
            )
            post = instaloader.Post.from_shortcode(L.context, shortcode)
            
            if post.is_video:
                video_url = post.video_url
                caption = post.caption or "Instagram_Reel"
                title = re.sub(r'[^\w\s-]', '', caption).strip().replace(' ', '_')[:60] or "Instagram_Video"
                thumbnail = post.url
                
                return {
                    'success': True,
                    'title': title.replace('_', ' '),
                    'download_url': video_url,
                    'thumbnail': thumbnail,
                    'duration': f"{int(post.video_duration or 0)}s" if hasattr(post, 'video_duration') else "Vídeo Curto",
                    'quality': 'HD (Meta CDN)',
                    'extension': 'mp4',
                    'direct': True,
                    'source': 'Instagram (CDN Direto)'
                }
        except Exception as e:
            errors.append(f"Provedor Nativo: {str(e)}")

    # Provedor 2: RapidAPI (Backup)
    try:
        api_key = 'cabf0a23f0mshc6ba466efaeb4b7p133ac0jsn3e3a9c0f2c4b'
        encoded_url = urllib.parse.quote(url)
        headers = {
            'x-rapidapi-host': 'instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com',
            'x-rapidapi-key': api_key
        }
        res = requests.get(
            f'https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi?url={encoded_url}',
            headers=headers,
            timeout=8
        )
        if res.status_code == 200:
            data = res.json()
            if not data.get('error') and data.get('download_url'):
                caption = data.get('caption') or "Instagram_Video"
                title = re.sub(r'[^\w\s-]', '', caption).strip().replace(' ', '_')[:60] or "Instagram_Video"
                return {
                    'success': True,
                    'title': title.replace('_', ' '),
                    'download_url': data['download_url'],
                    'thumbnail': data.get('thumb'),
                    'duration': "Reel",
                    'quality': 'Máxima via API',
                    'extension': 'mp4',
                    'direct': True,
                    'source': 'Instagram (RapidAPI)'
                }
            else:
                errors.append(f"RapidAPI: {data.get('message', 'Sem download_url')}")
        else:
            errors.append(f"RapidAPI HTTP {res.status_code}")
    except Exception as e:
        errors.append(f"RapidAPI: {str(e)}")

    raise Exception(f"Não foi possível extrair o vídeo do Instagram. Falhas: {'; '.join(errors)}")

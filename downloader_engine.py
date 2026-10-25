from services.youtube_service import resolve_youtube
from services.instagram_service import resolve_instagram

def resolve_media(url, format_type='video'):
    """
    Roteador central que identifica o serviço correto (YouTube, Instagram ou outros)
    e retorna o link direto de streaming e metadados.
    """
    url_lower = url.lower()

    if 'instagram.com' in url_lower:
        return resolve_instagram(url, format_type=format_type)
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return resolve_youtube(url, format_type=format_type)
    else:
        # Fallback universal para TikTok, Twitter, Facebook e outros via yt-dlp
        return resolve_youtube(url, format_type=format_type)

from services.youtube_service import resolve_youtube, check_youtube_apify_status
from services.instagram_service import resolve_instagram

def resolve_media(url, format_type='video'):
    """
    Roteador central que identifica o serviço correto (YouTube, Instagram ou outros)
    e retorna o link direto de streaming ou tarefa assíncrona.
    """
    url_lower = url.lower()

    if 'instagram.com' in url_lower:
        return resolve_instagram(url, format_type=format_type)
    elif 'youtube.com' in url_lower or 'youtu.be' in url_lower:
        return resolve_youtube(url, format_type=format_type)
    else:
        # Fallback universal para TikTok, Twitter, Facebook e outros
        return resolve_youtube(url, format_type=format_type)

def check_media_status(run_id, platform='youtube', format_type='video'):
    """
    Consulta o status de tarefas assíncronas (como Apify para YouTube).
    """
    return check_youtube_apify_status(run_id, format_type=format_type)

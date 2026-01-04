from .base import BaseParser
from .facebook import FacebookParser
# from .instagram import InstagramParser
# from .whatsapp import WhatsAppParser

def get_parser(platform: str, root_dir: str) -> BaseParser:
    """
    Factory to return the correct parser instance.
    """
    platform = platform.lower()
    
    if platform == 'facebook':
        return FacebookParser(root_dir)
    elif platform == 'instagram':
        # Instagram export is identical structure to Facebook
        from .instagram import InstagramParser
        return InstagramParser(root_dir)
    elif platform == 'whatsapp':
        from .whatsapp import WhatsAppParser
        return WhatsAppParser(root_dir)
    else:
        raise ValueError(f"Unsupported platform: {platform}")

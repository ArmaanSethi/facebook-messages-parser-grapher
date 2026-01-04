from .facebook import FacebookParser

class InstagramParser(FacebookParser):
    """
    Instagram data exports from Meta use the exact same JSON schema as Facebook Messenger.
    We reuse the FacebookParser logic entirey.
    
    The file structure might differ slightly (e.g. 'messages/inbox' vs just 'messages'),
    but since FacebookParser recurses via `rglob("message_*.json")`, it should handle it automatically.
    """
    pass

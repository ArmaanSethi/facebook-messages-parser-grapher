import ijson
from pathlib import Path
from typing import Generator, Dict, Any, List
import ftfy
from .base import BaseParser

class FacebookParser(BaseParser):
    def iter_conversations(self) -> Generator[Dict[str, Any], None, None]:
        """
        Streams conversations from the Facebook JSON export.
        Handles both 'inbox' and 'archived_threads' folders if they exist.
        """
        search_paths = [
            self.root_dir / "messages" / "inbox",
            self.root_dir / "messages" / "archived_threads",
            self.root_dir / "messages" / "e2ee_cutover",
            self.root_dir / "inbox",
            self.root_dir / "archived_threads",
            self.root_dir / "e2ee_cutover" 
        ]
        
        for folder in search_paths:
            if not folder.exists():
                continue
                
            for file_path in folder.rglob("message_*.json"):
                # We only want message_1.json usually, as others are continuations 
                # but for simplicity in this MVP we stream all. 
                # (Note: split files logic is complex, usually we just parse them all independently 
                # and let the Processor dedupe or merge if needed. 
                # For Facebook, message_2.json is just older messages of same thread.)
                
                try:
                    yield from self._parse_file(file_path)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

    def _parse_file(self, file_path: Path) -> Generator[Dict[str, Any], None, None]:
        """Parse a single message JSON file and yield conversation data."""
        title = self._get_title(file_path)
        
        # We need to materialize a batch of messages or yield them.
        # The BaseParser interface implies we yield "Conversations".
        # If a conversation is 1GB, we can't yield it as one dict.
        # But 'message_1.json' is max 100MB usually. So loading one file into memory is OK.
        # The issue is loading ALL files.
        # So yielding one file's content as a dict is safe.
        
        messages = []
        with open(file_path, 'rb') as f:
            for msg in ijson.items(f, 'messages.item'):
                # fix encoding
                if 'content' in msg:
                    msg['content'] = ftfy.fix_text(msg['content'])
                if 'sender_name' in msg:
                    msg['sender_name'] = ftfy.fix_text(msg['sender_name'])
                # fix reactions encoding
                if 'reactions' in msg:
                    for r in msg['reactions']:
                        if 'reaction' in r:
                            r['reaction'] = ftfy.fix_text(r['reaction'])
                        if 'actor' in r:
                            r['actor'] = ftfy.fix_text(r['actor'])
                            
                messages.append(msg)
                
        yield {
            'title': title,
            'messages': messages, # In-memory list for this single file
            'file': file_path.name
        }

    def _get_title(self, path: Path) -> str:
        """Fast scan for title using ijson without loading whole file."""
        try:
            with open(path, 'rb') as f:
                parser = ijson.parse(f)
                for prefix, event, value in parser:
                    if prefix == 'title':
                        return ftfy.fix_text(value)
        except (IOError, ijson.JSONError) as e:
            print(f"Warning: Could not parse title from {path.name}: {e}")
        return "Unknown"

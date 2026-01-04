from .base import BaseParser
from typing import Generator, Dict, Any, List
from pathlib import Path
import re
from datetime import datetime
import ftfy

# Optional: flexible date parsing
try:
    from dateutil import parser as date_parser
    HAS_DATEUTIL = True
except ImportError:
    HAS_DATEUTIL = False

class WhatsAppParser(BaseParser):
    def iter_conversations(self) -> Generator[Dict[str, Any], None, None]:
        """
        Parses WhatsApp .txt exports.
        Looks for all .txt files in the root_dir.
        """
        # WhatsApp exports are usually named "_chat.txt" inside a folder named "WhatsApp Chat - Name"
        # Or just "WhatsApp Chat with Name.txt"
        
        for file_path in self.root_dir.rglob("*.txt"):
            # Skipping internal system files or tiny files
            if file_path.name.startswith(".") or file_path.stat().st_size < 100:
                continue
                
            try:
                yield self._parse_file(file_path)
            except Exception as e:
                print(f"Error parsing WhatsApp log {file_path}: {e}")

    def _parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parses a single WhatsApp text file.
        """
        # Determine Title from filename
        # "WhatsApp Chat with Jane Doe.txt" -> "Jane Doe"
        title = file_path.stem.replace("WhatsApp Chat with ", "").replace("_chat", "")
        if title == "_chat":
            # Try parent folder name
            title = file_path.parent.name.replace("WhatsApp Chat - ", "")
            
        messages = []
        
        # Regex for standard WhatsApp format
        # [12/21/20, 10:59:03 PM] Sender: Message
        # Or non-bracket: 12/21/20, 10:59 PM - Sender: Message
        
        # We will support the Bracket format (iOS/Export standard) for now.
        # Format: [M/D/YY, H:MM:SS AM/PM] Sender: Content
        
        pattern = re.compile(r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s(\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AP]M)?)\]\s(.*?):\s(.*)$')
        
        # Fallback pattern (Android?): 05/12/2023, 14:02 - Sender: Message
        pattern_android = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s(\d{1,2}:\d{2})\s-\s(.*?):\s(.*)$')

        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                # Fix encoding immediately
                line = ftfy.fix_text(line)
                
                # Check match
                match = pattern.match(line)
                if not match:
                    match = pattern_android.match(line)
                    
                if match:
                    date_str, time_str, sender, content = match.groups()
                    
                    # Parse timestamp
                    ts_ms = 0
                    dt_string = f"{date_str} {time_str}"
                    
                    if HAS_DATEUTIL:
                        try:
                            dt = date_parser.parse(dt_string)
                            ts_ms = int(dt.timestamp() * 1000)
                        except (ValueError, TypeError):
                            ts_ms = 0
                    else:
                        # Manual fallback for common formats
                        for fmt in ["%m/%d/%y %I:%M:%S %p", "%d/%m/%Y %H:%M", "%m/%d/%y %I:%M %p"]:
                            try:
                                dt = datetime.strptime(dt_string, fmt)
                                ts_ms = int(dt.timestamp() * 1000)
                                break
                            except ValueError:
                                continue

                    messages.append({
                        'sender_name': sender,
                        'timestamp_ms': ts_ms,
                        'content': content,
                        'type': 'Generic'
                    })
                else:
                    # Multiline message handling
                    # If line doesn't start with date, append to previous msg content
                    if messages:
                        messages[-1]['content'] += f"\n{line}"
                        
        return {
            'title': title,
            'messages': messages,
            'file': file_path.name
        }

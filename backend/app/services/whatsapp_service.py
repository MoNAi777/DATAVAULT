import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from app.schemas.message import MessageCreate

logger = logging.getLogger(__name__)


class WhatsAppParser:
    """Parse WhatsApp exported chat files"""
    
    def __init__(self):
        # Common WhatsApp date formats - updated to handle more formats
        self.date_patterns = [
            # Israeli/Hebrew format: 6.4.2025, 11:18 - Name: Message
            r'^(\d{1,2}\.\d{1,2}\.\d{4}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            # US format: 12/25/22, 3:30 PM - Name: Message
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?:\s*[APap][Mm])?)\s*-\s*([^:]+):\s*(.+)$',
            # Bracketed format: [12/25/22, 3:30:45 PM] Name: Message
            r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?\s*[APap][Mm])\]\s*([^:]+):\s*(.+)$',
            # European format: 25/12/2022, 15:30 - Name: Message
            r'^(\d{1,2}/\d{1,2}/\d{4}),?\s+(\d{1,2}:\d{2})\s*-\s*([^:]+):\s*(.+)$',
            # Alternative Israeli format: 6.4.2025, 11:18 - Name: Message
            r'^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s+(\d{1,2}:\d{2}(?::\d{2})?)\s*-\s*([^:]+):\s*(.+)$',
        ]
        
        # System message patterns
        self.system_patterns = [
            r'Messages and calls are end-to-end encrypted',
            r'created group',
            r'added',
            r'removed',
            r'left',
            r'changed',
            r'security code changed',
            r'blocked this contact',
            r'unblocked this contact',
            # Hebrew system messages
            r'הודעות ושיחות מוצפנות מקצה לקצה',
            r'יצר קבוצה',
            r'הוסיף',
            r'הסיר',
            r'עזב',
            r'שינה',
        ]
    
    def parse_file(self, file_content: str, chat_name: str = "WhatsApp Chat") -> List[MessageCreate]:
        """Parse WhatsApp export file and return list of messages"""
        messages = []
        lines = file_content.split('\n')
        
        current_message = None
        
        logger.info(f"Starting to parse file with {len(lines)} lines")
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Try to parse as new message
            parsed = self._parse_message_line(line)
            
            if parsed:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                # Start new message
                date_str, time_str, sender, content = parsed
                timestamp = self._parse_datetime(date_str, time_str)
                
                # Skip system messages
                if self._is_system_message(content):
                    logger.debug(f"Skipping system message: {content[:50]}")
                    current_message = None
                    continue
                
                current_message = MessageCreate(
                    content=content,
                    source_type="whatsapp",
                    source_chat_id=chat_name,
                    source_message_id=f"whatsapp_{len(messages)}",
                    sender_name=sender.strip(),
                    sender_id=sender.strip().lower().replace(' ', '_'),
                    timestamp=timestamp,
                    message_type=self._detect_message_type(content)
                )
                logger.debug(f"Parsed message {len(messages)}: {sender} - {content[:50]}")
            else:
                # Continuation of previous message
                if current_message:
                    current_message.content += f"\n{line}"
                else:
                    # Log lines that couldn't be parsed for debugging
                    logger.debug(f"Could not parse line {i}: {line[:100]}")
        
        # Don't forget last message
        if current_message:
            messages.append(current_message)
        
        logger.info(f"Parsed {len(messages)} messages from WhatsApp export")
        return messages
    
    def _parse_message_line(self, line: str) -> Optional[Tuple[str, str, str, str]]:
        """Try to parse a message line with different patterns"""
        for pattern in self.date_patterns:
            match = re.match(pattern, line)
            if match:
                logger.debug(f"Matched pattern: {pattern[:50]}... for line: {line[:50]}")
                return match.groups()
        return None
    
    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        """Parse date and time strings to datetime object"""
        # Clean up the strings
        date_str = date_str.strip()
        time_str = time_str.strip()
        
        # Common formats to try - updated for Israeli format
        datetime_formats = [
            # Israeli format: 6.4.2025 11:18
            "%d.%m.%Y %H:%M",
            "%d.%m.%y %H:%M",
            # US formats
            "%m/%d/%y %I:%M %p",
            "%m/%d/%Y %I:%M %p",
            "%d/%m/%Y %H:%M",
            "%d/%m/%y %H:%M",
            "%m/%d/%y %I:%M:%S %p",
            "%d/%m/%Y %I:%M %p",
        ]
        
        # Combine date and time
        datetime_str = f"{date_str} {time_str}"
        
        for fmt in datetime_formats:
            try:
                parsed_dt = datetime.strptime(datetime_str, fmt)
                logger.debug(f"Successfully parsed datetime: {datetime_str} with format: {fmt}")
                return parsed_dt
            except ValueError:
                continue
        
        # If all fails, return current time
        logger.warning(f"Could not parse datetime: {datetime_str}")
        return datetime.utcnow()
    
    def _is_system_message(self, content: str) -> bool:
        """Check if message is a system message"""
        content_lower = content.lower()
        return any(pattern.lower() in content_lower for pattern in self.system_patterns)
    
    def _detect_message_type(self, content: str) -> str:
        """Detect message type from content"""
        content_lower = content.lower()
        
        if '<media omitted>' in content_lower:
            return 'media'
        elif 'image omitted' in content_lower:
            return 'image'
        elif 'video omitted' in content_lower:
            return 'video'
        elif 'audio omitted' in content_lower:
            return 'audio'
        elif 'document omitted' in content_lower:
            return 'document'
        elif '.pdf' in content_lower or '.doc' in content_lower:
            return 'document'
        elif 'http://' in content or 'https://' in content:
            return 'link'
        else:
            return 'text'


class WhatsAppService:
    """Service for handling WhatsApp imports"""
    
    def __init__(self):
        self.parser = WhatsAppParser()
        self.logger = logging.getLogger(__name__)
    
    async def import_chat_file(
        self, 
        file_content: str, 
        chat_name: str,
        user_id: Optional[str] = None
    ) -> Dict[str, any]:
        """Import WhatsApp chat from exported file"""
        try:
            # Log first few lines for debugging
            lines = file_content.split('\n')[:5]
            self.logger.info(f"First 5 lines of file: {lines}")
            
            # Parse messages
            messages = self.parser.parse_file(file_content, chat_name)
            
            if not messages:
                return {
                    "success": False,
                    "error": "No messages found in file. Please check the file format.",
                    "imported": 0
                }
            
            # Import messages to database
            from app.services.message_service import MessageService
            message_service = MessageService()
            
            imported = 0
            errors = []
            
            for message in messages:
                try:
                    # Add user_id if provided
                    if user_id:
                        message.sender_id = f"{user_id}_{message.sender_id}"
                    
                    await message_service.create_message(message)
                    imported += 1
                except Exception as e:
                    self.logger.error(f"Error importing message: {e}")
                    errors.append(str(e))
            
            return {
                "success": True,
                "imported": imported,
                "total": len(messages),
                "errors": errors[:5]  # Return first 5 errors
            }
            
        except Exception as e:
            self.logger.error(f"Error importing WhatsApp chat: {e}")
            return {
                "success": False,
                "error": str(e),
                "imported": 0
            } 
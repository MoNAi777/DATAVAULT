from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import logging

from app.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])
logger = logging.getLogger(__name__)


@router.post("/import")
async def import_whatsapp_chat(
    file: UploadFile = File(...),
    chat_name: str = Form(...),
    user_id: Optional[str] = Form(None)
):
    """Import WhatsApp chat from exported .txt file"""
    try:
        # Validate file type
        if not file.filename.endswith('.txt'):
            raise HTTPException(
                status_code=400,
                detail="Please upload a .txt file exported from WhatsApp"
            )
        
        # Read file content
        content = await file.read()
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            # Try with different encoding
            file_content = content.decode('utf-8-sig', errors='ignore')
        
        # Import messages
        whatsapp_service = WhatsAppService()
        result = await whatsapp_service.import_chat_file(
            file_content=file_content,
            chat_name=chat_name,
            user_id=user_id
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to import chat")
            )
        
        return {
            "success": True,
            "message": f"Successfully imported {result['imported']} messages from {chat_name}",
            "details": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error importing WhatsApp chat: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal error: {str(e)}"
        )


@router.get("/parse-instructions")
async def get_parse_instructions():
    """Get instructions for exporting WhatsApp chats"""
    return {
        "instructions": {
            "android": [
                "1. Open WhatsApp and go to the chat you want to export",
                "2. Tap the three dots menu (⋮) in the top right",
                "3. Select 'More' → 'Export chat'",
                "4. Choose 'Without Media' (recommended) or 'Include Media'",
                "5. Save the .txt file and upload it here"
            ],
            "ios": [
                "1. Open WhatsApp and go to the chat you want to export",
                "2. Tap the contact name at the top",
                "3. Scroll down and tap 'Export Chat'",
                "4. Choose 'Without Media' (recommended) or 'Include Media'",
                "5. Save the .txt file and upload it here"
            ],
            "tips": [
                "Export without media for faster processing",
                "You can export group chats too",
                "The file must be in .txt format",
                "All messages will be processed with AI for categorization and insights"
            ]
        }
    } 
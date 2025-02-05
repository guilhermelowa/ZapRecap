from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from app.services.text_analyzer import calculate_all_metrics, parse_whatsapp_chat, calculate_conversation_parts, extract_themes
from app.services.chatgpt_utils import simulate_author_message
from app.models.data_formats import Message, ConversationThemesResponse, SimulatedMessageResponse
from typing import List
import mercadopago
import os
from dotenv import load_dotenv
import logging
import uuid
from functools import lru_cache
from app.core.config import get_settings, clear_settings_cache
from app.utils.cache_manager import CacheManager
from sqlalchemy.orm import Session
from ..database import get_db, Suggestion, ParsedConversation
from datetime import datetime, timedelta
from ..auth.security import verify_token, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..auth.models import Admin
from hashlib import sha256
import json
from sqlalchemy.exc import IntegrityError

# Load environment variables from .env file in development
if os.getenv('ENVIRONMENT') != 'production':
    load_dotenv()

logger = logging.getLogger(__name__)

class FileRequest(BaseModel):
    content: str

class SimulationRequest(BaseModel):
    conversation: List[Message]
    author: str
    prompt: str
    language: str = 'pt'

class PaymentRequest(BaseModel):
    amount: float
    description: str

class PaymentResponse(BaseModel):
    payment_id: str
    qr_code: str
    copy_cola: str

class PaymentStatus(BaseModel):
    status: str

class SuggestionCreate(BaseModel):
    suggestion: str
    conversation_id: str | None = None
    timestamp: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class AdminLogin(BaseModel):
    username: str
    password: str

# Use the client in your routes
router = APIRouter()
clear_settings_cache()
settings = get_settings()
mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

# Initialize router and cache
chat_cache = CacheManager(max_size=100, expiration_minutes=30)

def message_to_dict(msg: Message) -> dict:
    return {
        "date": msg.date.isoformat(),
        "author": msg.author,
        "content": msg.content
    }

@router.post("/analyze")
async def analyze(request: Request, file: FileRequest, db: Session = Depends(get_db)):
    logger.info(f"Analyze endpoint hit with content length: {len(file.content)}")
    try:
        content_hash = sha256(file.content.encode()).hexdigest()
        
        parsed_conv = db.query(ParsedConversation).filter(
            ParsedConversation.content_hash == content_hash
        ).first()
        
        if not parsed_conv:
            dates, author_and_messages, conversation = parse_whatsapp_chat(file.content)
            
            # Convert Message objects to dictionaries before JSON serialization
            parsed_conv = ParsedConversation(
                content_hash=content_hash,
                dates=json.dumps([d.isoformat() for d in dates]),
                author_and_messages=json.dumps({
                    author: [message_to_dict(msg) for msg in messages]
                    for author, messages in author_and_messages.items()
                }),
                conversation=json.dumps([message_to_dict(msg) for msg in conversation])
            )
            
            try:
                db.add(parsed_conv)
                db.commit()
                db.refresh(parsed_conv)
            except IntegrityError:
                db.rollback()
                parsed_conv = db.query(ParsedConversation).filter(
                    ParsedConversation.content_hash == content_hash
                ).first()
        
        result = calculate_all_metrics(file.content)
        # Use content_hash as conversation identifier
        result.conversation_id = content_hash
        logger.info("Analysis completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise

@router.post("/conversation-themes", response_model=ConversationThemesResponse)
async def get_conversation_themes(request: Request, file: FileRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Conversation themes endpoint hit with content length: {len(file.content)}")
        
        content_hash = sha256(file.content.encode()).hexdigest()
        parsed_conv = db.query(ParsedConversation).filter(
            ParsedConversation.content_hash == content_hash
        ).first()
        
        if parsed_conv:
            # Load data from database
            logger.info("Found existing conversation in database")
            dates = [datetime.fromisoformat(d) for d in json.loads(parsed_conv.dates)]
            author_and_messages = json.loads(parsed_conv.author_and_messages)
            conversation = json.loads(parsed_conv.conversation)
            logger.info(f"Loaded conversation with {len(conversation)} messages")
        else:
            # Parse and store new conversation
            logger.info("Parsing new conversation")
            dates, author_and_messages, conversation = parse_whatsapp_chat(file.content)
            logger.info(f"Parsed conversation with {len(conversation)} messages")
            
            parsed_conv = ParsedConversation(
                content_hash=content_hash,
                dates=json.dumps([d.isoformat() for d in dates]),
                author_and_messages=json.dumps(author_and_messages),
                conversation=json.dumps(conversation)
            )
            
            try:
                db.add(parsed_conv)
                db.commit()
                db.refresh(parsed_conv)
            except IntegrityError:
                db.rollback()
        
        _, _, _, max_conversation, _ = calculate_conversation_parts(conversation)
        logger.info(f"Max conversation length: {len(max_conversation) if max_conversation else 0}")
        themes = extract_themes(max_conversation)
        logger.info(f"Extracted themes: {themes}")
        
        if not themes:
            logger.warning("No themes were extracted")
            
        return ConversationThemesResponse(themes=themes)
    except Exception as e:
        logger.error(f"Error getting conversation themes: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-message", response_model=SimulatedMessageResponse)
async def simulate_message(request: SimulationRequest):
    logger.info("Message simulation endpoint hit")
    try:
        simulated_message = simulate_author_message(
            request.author,
            request.conversation,
            request.prompt,
            request.language
        )
        return SimulatedMessageResponse(simulated_message=simulated_message)
    except Exception as e:
        logger.error(f"Error simulating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-pix-payment", response_model=PaymentResponse)
async def create_pix_payment(payment: PaymentRequest):
    try:
        logger.info(f"Creating payment for amount: {payment.amount}")
        # Verify SDK initialization
        if not mp:
            logger.error("MercadoPago SDK not initialized")
            raise HTTPException(status_code=500, detail="Payment service not initialized")
            
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'X-Idempotency-Key': str(uuid.uuid4()),
        }
        
        payment_data = {
            "transaction_amount": payment.amount,
            "description": payment.description,
            "payment_method_id": "pix",
            "payer": {
                "email": "guiga994@gmail.com",
                "first_name": "Guilherme",
                "last_name": "Wanderley",
                "identification": {
                    "type": "CPF",
                    "number": "01668100533"
                },
                "address": {
                    "zip_code": "44077090",
                    "street_name": "Rua Saracura",
                    "street_number": "622",
                    "neighborhood": "Santa Mônica",
                    "city": "Feira de Santana",
                    "federal_unit": "BA"
                }
            }
        }
        
        payment_result = mp.payment().create(payment_data, request_options)
        payment_result = payment_result["response"]
        logger.info(f"Created payment with ID: {payment_result['id']}")
        
        return PaymentResponse(
            payment_id=str(payment_result["id"]),
            qr_code=payment_result["point_of_interaction"]["transaction_data"]["qr_code_base64"],
            copy_cola=payment_result["point_of_interaction"]["transaction_data"]["qr_code"]
        )
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/check-payment-status/{payment_id}", response_model=PaymentStatus)
async def check_payment_status(payment_id: str):
    try:
        if (type(payment_id) == int):
            payment_id = str(payment_id)
        # logger.info(f"Checking payment status for ID: {payment_id}")
        payment = mp.payment().get(payment_id)
        payment_data = payment["response"]
        # logger.info(f"Payment status: {payment_data['status']}")
        return PaymentStatus(status=payment_data["status"])
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/suggestions")
def create_suggestion(
    suggestion: SuggestionCreate,
    db: Session = Depends(get_db)
):
    db_suggestion = Suggestion(
        suggestion=suggestion.suggestion,
        conversation_id=suggestion.conversation_id,
        timestamp=suggestion.timestamp
    )
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return {"status": "success"}

@router.get("/admin/suggestions", response_model=List[dict])
def list_suggestions(
    status: str = None,
    days: int = None,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    query = db.query(Suggestion)
    
    if status:
        query = query.filter(Suggestion.status == status)
    
    if days:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        query = query.filter(Suggestion.timestamp >= cutoff_date)
    
    suggestions = query.all()
    return [
        {
            "id": s.id,
            "suggestion": s.suggestion,
            "conversation_id": s.conversation_id,
            "timestamp": s.timestamp,
            "status": s.status
        }
        for s in suggestions
    ]

@router.put("/admin/suggestions/{suggestion_id}")
def update_suggestion_status(
    suggestion_id: int,
    status: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token)
):
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    
    suggestion.status = status
    db.commit()
    return {"status": "success"}

@router.post("/login", response_model=Token)
def login(login_data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == login_data.username).first()
    if not admin or not verify_password(login_data.password, admin.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(
        data={"sub": admin.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}
from fastapi import APIRouter, HTTPException, Depends, Security, Query, File, UploadFile
from pydantic import BaseModel, Field
from app.services.text_analyzer import calculate_all_metrics
from app.services.chatgpt_utils import (
    simulate_author_message,
    extract_themes,
    parse_themes_response,
)
from app.models.data_formats import (
    Message,
    ConversationThemesResponse,
    SimulatedMessageResponse,
)
from typing import List, Union, Optional
import mercadopago
import os
from dotenv import load_dotenv
import logging
import uuid
from app.core.config import get_settings, clear_settings_cache
from app.utils.cache_manager import CacheManager
from sqlalchemy.orm import Session
from app.models.database_models import Suggestion, ParsedConversation
from app.database import get_db
from datetime import datetime, timedelta
from ..auth.security import verify_token, verify_password, create_access_token
from ..auth.models import Admin
import json
from app.services.parsing_utils import get_or_create_parsed_conversation, extract_file_content

# Load environment variables from .env file in development
if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

logger = logging.getLogger(__name__)


class FileRequest(BaseModel):
    content: str = Field(..., min_length=1)


class SimulationRequest(BaseModel):
    conversation: List[Message]
    author: str = Field(..., min_length=1)
    prompt: str = Field(..., min_length=1)
    language: str = Field(default="pt")
    model: str = Field(...)


class PaymentRequest(BaseModel):
    amount: float = Field(..., gt=0)
    description: str = Field(..., min_length=1)


class PaymentResponse(BaseModel):
    payment_id: str
    qr_code: str
    copy_cola: str


class PaymentStatus(BaseModel):
    status: str


class SuggestionCreate(BaseModel):
    suggestion: str
    conversation_id: Union[str, None] = None
    timestamp: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class AdminLogin(BaseModel):
    username: str
    password: str


class ConversationThemesRequest(BaseModel):
    conversation_id: str
    model: str


class AdminRegister(BaseModel):
    username: str
    password: str
    registration_token: str


# Use the client in your routes
router = APIRouter()
clear_settings_cache()
settings = get_settings()
mp = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

# Initialize router and cache
chat_cache = CacheManager(max_size=100, expiration_minutes=30)


def message_to_dict(msg: Message) -> dict:
    return {"date": msg.date.isoformat(), "author": msg.author, "content": msg.content}


@router.post("/analyze")
async def analyze(file: UploadFile = File(...), db: Session = Depends(get_db)):
    logger.info(f"Analyze endpoint hit with file: {file.filename}")

    try:
        # Extract and validate file content
        file_content = await extract_file_content(file)
        logger.info(f"Analyze endpoint processing content length: {len(file_content)}")

        try:
            (
                dates,
                author_and_messages,
                conversation,
                content_hash,
            ) = get_or_create_parsed_conversation(file_content, db)

            result = calculate_all_metrics(dates, author_and_messages, conversation, content_hash)
            return result
        except (ValueError, IndexError, AttributeError) as e:
            logger.error(f"Error parsing chat content: {str(e)}")
            raise HTTPException(
                status_code=400, detail="Error analyzing conversation: Invalid WhatsApp chat format"
            )
        except Exception as db_e:
            logger.error(f"Database error during analysis: {str(db_e)}")
            raise HTTPException(
                status_code=500, detail="Database error during conversation analysis"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/conversation-themes", response_model=ConversationThemesResponse)
async def get_conversation_themes(
    request: ConversationThemesRequest, db: Session = Depends(get_db)
):
    try:
        logger.info(
            f"Conversation themes endpoint hit for \
                conversation: {request.conversation_id} \
                and model {request.model}"
        )

        try:
            parsed_conv = (
                db.query(ParsedConversation)
                .filter(ParsedConversation.content_hash == request.conversation_id)
                .first()
            )
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            raise HTTPException(status_code=503, detail="Database service unavailable")

        if not parsed_conv:
            raise HTTPException(status_code=404, detail="Conversation not found")

        conversation = [Message.model_validate(msg) for msg in json.loads(parsed_conv.conversation)]
        logger.info(f"Loaded conversation with {len(conversation)} messages")

        # Theme Extraction
        themes = extract_themes(conversation, model=request.model)
        logger.info(f"Extracted themes: {themes}")

        if not themes:
            logger.warning("No themes extracted from LLM")
            raise HTTPException(status_code=422, detail="No themes extracted from LLM")

        # Theme Parsing
        parsed_themes = parse_themes_response(themes)
        logger.info(f"Parsed themes: {parsed_themes}")

        if not parsed_themes:
            logger.warning(f"Parsing {themes} resulted in no themes")
            raise HTTPException(status_code=422, detail="Unable to parse extracted themes")

        return ConversationThemesResponse(themes=parsed_themes)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in conversation themes: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/simulate-message", response_model=SimulatedMessageResponse)
async def simulate_message(request: SimulationRequest):
    logger.info(
        f"Message simulation endpoint hit using \
                model {request.model}\
                prompt {request.prompt}\
                author {request.author}"
    )
    try:
        # Ensure conversation messages are proper Message objects.
        conversation = [
            msg if isinstance(msg, Message) else Message.model_validate(msg)
            for msg in request.conversation
        ]
        simulated_message = simulate_author_message(
            conversation,
            request.author,
            request.prompt,
            request.language,
            model=request.model,
        )
        return SimulatedMessageResponse(simulated_message=simulated_message)
    except Exception as e:
        logger.error(f"Error simulating message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create-pix-payment", response_model=PaymentResponse)
async def create_pix_payment(payment: PaymentRequest):
    try:
        logger.info(f"Creating payment for amount: {payment.amount}")
        if not mp:
            raise HTTPException(status_code=503, detail="Payment service unavailable")

        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            "X-Idempotency-Key": str(uuid.uuid4()),
        }

        # Move sensitive data to environment variables or settings
        payment_data = {
            "transaction_amount": payment.amount,
            "description": payment.description,
            "payment_method_id": "pix",
            "payer": {
                "email": settings.PAYER_EMAIL,
                "first_name": settings.PAYER_FIRST_NAME,
                "last_name": settings.PAYER_LAST_NAME,
                "identification": {
                    "type": settings.PAYER_ID_TYPE,
                    "number": settings.PAYER_ID_NUMBER,
                },
                "address": settings.PAYER_ADDRESS,
            },
        }

        payment_result = mp.payment().create(payment_data, request_options)
        if "response" not in payment_result:
            raise HTTPException(status_code=500, detail="Invalid payment service response")

        payment_result = payment_result["response"]
        return PaymentResponse(
            payment_id=str(payment_result["id"]),
            qr_code=payment_result["point_of_interaction"]["transaction_data"]["qr_code_base64"],
            copy_cola=payment_result["point_of_interaction"]["transaction_data"]["qr_code"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process payment")


@router.get("/check-payment-status/{payment_id}", response_model=PaymentStatus)
async def check_payment_status(payment_id: str):
    try:
        if isinstance(payment_id, int):
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
def create_suggestion(suggestion: SuggestionCreate, db: Session = Depends(get_db)):
    db_suggestion = Suggestion(
        suggestion=suggestion.suggestion,
        conversation_id=suggestion.conversation_id,
        timestamp=suggestion.timestamp,
    )
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return {"status": "success"}


@router.get("/admin/suggestions", response_model=List[dict])
def list_suggestions(
    status: Optional[str] = None,
    days: Optional[int] = Query(default=None, ge=1, le=365),
    db: Session = Depends(get_db),
    username: str = Security(verify_token),
):
    try:
        query = db.query(Suggestion)

        if status:
            if status not in ["pending", "approved", "rejected"]:
                raise HTTPException(status_code=400, detail="Invalid status value")
            query = query.filter(Suggestion.status == status)

        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = query.filter(Suggestion.timestamp >= cutoff_date)

        suggestions = query.all()
        return [suggestion.to_dict() for suggestion in suggestions]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve suggestions")


@router.put("/admin/suggestions/{suggestion_id}")
def update_suggestion_status(
    suggestion_id: int,
    status: str,
    db: Session = Depends(get_db),
    username: str = Depends(verify_token),
):
    suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    suggestion.status = status
    db.commit()
    return {"status": "success"}


@router.post("/login", response_model=Token)
async def login(login_data: AdminLogin, db: Session = Depends(get_db)):
    try:
        admin = db.query(Admin).filter(Admin.username == login_data.username).first()

        if not admin or not verify_password(login_data.password, admin.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect username or password")

        access_token = create_access_token(
            data={"sub": admin.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise HTTPException(status_code=500, detail="Login process failed")

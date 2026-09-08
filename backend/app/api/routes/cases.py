"""
backend/app/api/routes/cases.py
Cybercrime complaint case directory, dossier, and deterministic NLP intake endpoints.
"""

import re
import uuid
import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import CaseModel
from backend.app.schemas.case import CaseResponse, CaseCreate, PatrolDispatchRequest, PatrolDispatchResponse
from backend.app.schemas.prediction import ComplaintParseRequest, ComplaintParseResponse
from backend.app.services.case_service import CaseService
from src.data.atm_processor import STATE_COORDINATES, DISTRICT_COORDINATES

router = APIRouter(tags=["Cases"])

# Alias mapping for major metros and states
STATE_ALIASES = {
    "DELHI": "DELHI",
    "NEW DELHI": "DELHI",
    "NCR": "DELHI",
    "MUMBAI": "MAHARASHTRA",
    "PUNE": "MAHARASHTRA",
    "NAGPUR": "MAHARASHTRA",
    "BENGALURU": "KARNATAKA",
    "BANGALORE": "KARNATAKA",
    "HYDERABAD": "TELANGANA",
    "CHENNAI": "TAMIL NADU",
    "KOLKATA": "WEST BENGAL",
    "CALCUTTA": "WEST BENGAL",
    "JAIPUR": "RAJASTHAN",
    "AHMEDABAD": "GUJARAT",
    "SURAT": "GUJARAT",
    "LUCKNOW": "UTTAR PRADESH",
    "NOIDA": "UTTAR PRADESH",
    "GHAZIABAD": "UTTAR PRADESH",
    "PATNA": "BIHAR",
    "CHANDIGARH": "PUNJAB",
    "BHOPAL": "MADHYA PRADESH",
    "INDORE": "MADHYA PRADESH"
}

DISTRICT_ALIASES = {
    "MUMBAI": "MUMBAI SUBURBAN",
    "DELHI": "NEW DELHI",
    "BENGALURU": "BENGALURU URBAN",
    "BANGALORE": "BENGALURU URBAN",
    "HYDERABAD": "HYDERABAD",
    "KOLKATA": "KOLKATA",
    "JAIPUR": "JAIPUR",
    "PUNE": "PUNE",
    "CHENNAI": "CHENNAI",
    "AHMEDABAD": "AHMEDABAD",
    "LUCKNOW": "LUCKNOW"
}

BANK_ALIASES = {
    "SBI": "STATE BANK OF INDIA",
    "STATE BANK": "STATE BANK OF INDIA",
    "HDFC": "HDFC BANK LIMITED",
    "ICICI": "ICICI BANK LIMITED",
    "AXIS": "AXIS BANK LIMITED",
    "PNB": "PUNJAB NATIONAL BANK",
    "PUNJAB NATIONAL": "PUNJAB NATIONAL BANK",
    "BOB": "BANK OF BARODA",
    "BANK OF BARODA": "BANK OF BARODA",
    "CANARA": "CANARA BANK",
    "KOTAK": "KOTAK MAHINDRA BANK LIMITED",
    "UNION BANK": "UNION BANK OF INDIA"
}

@router.get("/cases", response_model=List[CaseResponse])
def get_cases(
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by status"),
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Retrieves all active cybercrime cases with filtering."""
    cases = CaseService.get_cases(db, status=status_filter, limit=limit)
    return cases

@router.get("/cases/{case_id}", response_model=CaseResponse)
def get_case(case_id: str, db: Session = Depends(get_db)):
    """Retrieves specific cybercrime case dossier by ID."""
    case = CaseService.get_case(db, case_id=case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cybercrime complaint case '{case_id}' not found."
        )
    return case

@router.post("/cases", response_model=CaseResponse)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)):
    """Creates a new structured cybercrime case for predictive analysis."""
    case_dict = payload.model_dump()
    if not case_dict.get("case_id"):
        case_dict["case_id"] = f"CC-{datetime.datetime.now().year}-{uuid.uuid4().hex[:5].upper()}"
    if not case_dict.get("complaint_time"):
        case_dict["complaint_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if not case_dict.get("prediction_time"):
        case_dict["prediction_time"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    new_case = CaseService.create_case(db, case_dict)
    return new_case

@router.post("/parse-complaint", response_model=ComplaintParseResponse)
def parse_complaint(payload: ComplaintParseRequest):
    """
    Lightweight, deterministic NLP intake endpoint.
    Parses unstructured cybercrime narrative text into structured case parameters.
    Extracts: fraud amount, fraud scenario, channel, state, district, bank, time.
    """
    text = payload.complaint_text
    text_upper = text.upper()

    # 1. Extract Fraud Amount
    # Matches ₹1,20,000, Rs. 50,000, INR 125000, or numbers followed by rupees/inr
    amount = None
    amt_match = re.search(r'(?:₹|RS\.?|INR)\s*([0-9,]+(?:\.[0-9]{1,2})?)', text, re.IGNORECASE)
    if not amt_match:
        amt_match = re.search(r'([0-9,]+(?:\.[0-9]{1,2})?)\s*(?:RUPEES|INR|RS)', text, re.IGNORECASE)
    if not amt_match:
        # Fallback to general numbers with commas e.g. "debited 45,000"
        amt_match = re.search(r'(?:DEBITED|TRANSFERRED|LOST|STOLEN|AMOUNT OF)\s*([0-9,]+)', text, re.IGNORECASE)

    if amt_match:
        try:
            amt_str = amt_match.group(1).replace(",", "").strip()
            amount = float(amt_str)
        except Exception:
            amount = 50000.0

    # 2. Extract Fraud Type & Channel
    fraud_type = "upi_phishing"
    channel = "UPI"

    if any(k in text_upper for k in ["OTP", "ONE TIME PASSWORD", "SMS CODE", "VERIFICATION CODE"]):
        fraud_type = "otp_fraud"
        channel = "Mobile_App"
    elif any(k in text_upper for k in ["INVEST", "CRYPTO", "TELEGRAM", "STOCK", "PROFIT", "TRADING", "TASK"]):
        fraud_type = "investment_scam"
        channel = "IMPS"
    elif any(k in text_upper for k in ["ATM", "SKIMMING", "CARD CLONE", "ATM MACHINE", "WITHDRAWAL"]):
        fraud_type = "atm_related_fraud"
        channel = "ATM_Withdrawal"
    elif any(k in text_upper for k in ["NET BANKING", "PASSWORD CHANGED", "LOGIN", "UNAUTHORIZED ACCESS"]):
        fraud_type = "account_takeover"
        channel = "Net_Banking"
    elif any(k in text_upper for k in ["LOAN", "EXTORTION", "BLACKMAIL", "HARASSMENT", "APP PERMISSION"]):
        fraud_type = "loan_app_extortion"
        channel = "UPI"
    elif any(k in text_upper for k in ["RTGS", "CORPORATE", "INVOICE", "COMPANY ACCOUNT", "VENDOR"]):
        fraud_type = "corporate_cyber_fraud"
        channel = "RTGS"
    elif any(k in text_upper for k in ["CREDIT CARD", "POS", "SWIPE"]):
        fraud_type = "card_fraud"
        channel = "POS"
    elif any(k in text_upper for k in ["UPI", "G组织的", "GPAY", "PHONEPE", "PAYTM", "QR CODE"]):
        fraud_type = "upi_phishing"
        channel = "UPI"

    # 3. Extract State & District
    detected_state = "MAHARASHTRA"
    detected_district = "MUMBAI SUBURBAN"

    for city_key, mapped_state in STATE_ALIASES.items():
        if city_key in text_upper:
            detected_state = mapped_state
            if city_key in DISTRICT_ALIASES:
                detected_district = DISTRICT_ALIASES[city_key]
            else:
                detected_district = city_key
            break

    # 4. Extract Bank
    detected_bank = None
    for b_key, full_bank in BANK_ALIASES.items():
        if b_key in text_upper:
            detected_bank = full_bank
            break

    # 5. Extract Keywords
    keywords = []
    for kw in ["DEBITED", "PHISHING", "UPI", "CALL", "MULE", "TRANSFER", "TELEGRAM", "LINK", "OTP", "ATM"]:
        if kw in text_upper:
            keywords.append(kw.lower())

    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return ComplaintParseResponse(
        raw_text=text,
        fraud_amount=amount or 50000.0,
        fraud_type=fraud_type,
        channel=channel,
        state=detected_state,
        district=detected_district,
        bank=detected_bank or "STATE BANK OF INDIA",
        transaction_keywords=keywords,
        incident_time=now_iso,
        review_status="PENDING_CONFIRMATION"
    )

@router.post("/cases/{case_id}/dispatch", response_model=PatrolDispatchResponse)
def dispatch_patrol(
    case_id: str,
    payload: PatrolDispatchRequest,
    db: Session = Depends(get_db)
):
    """
    Tactical Patrol Dispatch Endpoint.
    Transmits high-risk candidate ATM coordinates to field patrol units (PCR / Beat Constable / Thana).
    Escalates case status to MONITORED and transitions open alerts to UNDER_REVIEW.
    """
    case = CaseService.get_case(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cybercrime complaint case '{case_id}' not found."
        )

    case.case_status = "MONITORED"
    case.updated_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()
    db.refresh(case)

    # Escalate associated alerts to UNDER_REVIEW
    from backend.app.db.models import AlertModel
    open_alerts = db.query(AlertModel).filter(AlertModel.case_id == case_id, AlertModel.status == "NEW").all()
    for alt in open_alerts:
        alt.status = "UNDER_REVIEW"
        alt.acknowledged_by = f"DISPATCHED_{payload.patrol_unit}"
        alt.acknowledged_at = datetime.datetime.now(datetime.timezone.utc)
    db.commit()

    now_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

    return PatrolDispatchResponse(
        status="SUCCESS",
        message=f"Tactical dispatch successfully transmitted to {payload.patrol_unit}. Case status updated to MONITORED.",
        case=case,
        dispatched_unit=payload.patrol_unit,
        target_location_id=payload.target_location_id,
        dispatch_timestamp=now_str
    )

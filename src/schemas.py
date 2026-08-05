from typing import List, Optional
from pydantic import BaseModel, Field

# --- Sub-schemas ---

class SellerHandoff(BaseModel):
    seller_id: str
    shipping_limit_at: Optional[str] = None
    handoff_variance_hours: Optional[float] = None
    late_handoff: bool

class CaseAssessment(BaseModel):
    primary_issue: str
    secondary_issues: List[str] = Field(default_factory=list)
    case_status: str  # 'action_required' or 'no_action'
    confidence: float

class AffectedEntities(BaseModel):
    order_ids: List[str] = Field(default_factory=list)
    item_ids: List[str] = Field(default_factory=list)
    seller_ids: List[str] = Field(default_factory=list)
    payment_ids: List[str] = Field(default_factory=list)

class CustomerContext(BaseModel):
    customer_unique_id: str
    related_order_ids: List[str] = Field(default_factory=list)

class ProductContext(BaseModel):
    product_ids: List[str] = Field(default_factory=list)
    category_names: List[str] = Field(default_factory=list)

class DeliveryAnalysis(BaseModel):
    delivered_at: Optional[str] = None
    estimated_delivery_at: Optional[str] = None
    carrier_handoff_at: Optional[str] = None
    delivery_variance_hours: Optional[float] = None
    seller_handoff_analysis: List[SellerHandoff] = Field(default_factory=list)
    late_handoff_seller_ids: List[str] = Field(default_factory=list)

class PaymentReconciliation(BaseModel):
    currency: str = "BRL"
    item_total_brl: Optional[float] = None
    freight_total_brl: Optional[float] = None
    expected_total_brl: Optional[float] = None
    payment_total_brl: Optional[float] = None
    difference_brl: Optional[float] = None
    reconciled: Optional[bool] = None
    payment_types: List[str] = Field(default_factory=list)

class CauseCode(BaseModel):
    cause_code: str
    rank: int

class ResponsibleParty(BaseModel):
    party_type: str  # 'seller', 'logistics_provider', 'platform', etc.
    party_id: str

class RootCauseAnalysis(BaseModel):
    ranked_causes: List[CauseCode] = Field(default_factory=list)
    responsible_parties: List[ResponsibleParty] = Field(default_factory=list)

class FinancialResolution(BaseModel):
    currency: str = "BRL"
    recommended_refund_brl: float

# --- Final Case Output Schema ---

class CaseOutput(BaseModel):
    case_id: str
    case_assessment: CaseAssessment
    affected_entities: AffectedEntities
    customer_context: CustomerContext
    product_context: ProductContext
    delivery_analysis: DeliveryAnalysis
    payment_reconciliation: PaymentReconciliation
    root_cause_analysis: RootCauseAnalysis
    evidence_ids: List[str] = Field(default_factory=list)
    financial_resolution: FinancialResolution
    resolution_actions: List[str] = Field(default_factory=list)

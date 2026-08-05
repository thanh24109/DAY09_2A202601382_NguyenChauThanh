from decimal import Decimal
from typing import Annotated, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


Timestamp = Annotated[str, Field(pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")]
EntityId = Annotated[str, Field(pattern=r"^[0-9a-f]{32}$")]
CaseId = Annotated[str, Field(pattern=r"^EC_\d{3}$")]
ItemId = Annotated[str, Field(pattern=r"^[0-9a-f]{32}:\d+$")]
PaymentId = Annotated[str, Field(pattern=r"^[0-9a-f]{32}:\d+$")]
EvidenceId = Annotated[
    str,
    Field(
        pattern=(
            r"^(order:[0-9a-f]{32}|item:[0-9a-f]{32}:\d+|"
            r"payment:[0-9a-f]{32}:\d+|seller:[0-9a-f]{32}|"
            r"policy:[A-Z_]+)$"
        )
    ),
]

PrimaryIssue = Literal[
    "canceled_order_paid",
    "unavailable_order_paid",
    "late_delivery_seller",
    "late_delivery_logistics",
    "valid_split_payment",
    "unsupported_late_claim",
]
SecondaryIssue = Literal[
    "multi_item_order",
    "multi_seller_order",
    "split_payment",
    "repeat_customer",
    "multiple_categories",
]
CauseCodeValue = Literal[
    "SELLER_HANDOFF_AFTER_LIMIT",
    "CARRIER_DELIVERED_AFTER_ESTIMATE",
    "ORDER_CANCELED_AFTER_PAYMENT",
    "ORDER_UNAVAILABLE_AFTER_PAYMENT",
    "MULTIPLE_PAYMENTS_RECONCILED",
    "DELIVERY_WITHIN_ESTIMATE",
]
ResolutionAction = Literal[
    "issue_full_refund",
    "refund_freight",
    "explain_valid_split_payment",
    "reject_late_refund",
    "review_seller_handoff",
    "review_carrier_delay",
    "verify_refund_completion",
    "coordinate_multi_seller_case",
    "verify_payment_allocation",
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


def _has_at_most_two_decimals(value: Optional[float]) -> Optional[float]:
    if value is None:
        return value
    decimal_value = Decimal(str(value))
    if decimal_value != decimal_value.quantize(Decimal("0.01")):
        raise ValueError("monetary values must have at most two decimal places")
    return value


class SellerHandoff(StrictModel):
    seller_id: EntityId
    shipping_limit_at: Optional[Timestamp] = None
    handoff_variance_hours: Optional[float] = None
    late_handoff: bool

    @model_validator(mode="after")
    def validate_late_handoff(self):
        if self.handoff_variance_hours is None and self.late_handoff:
            raise ValueError("late_handoff cannot be true without a variance")
        if self.handoff_variance_hours is not None:
            if self.late_handoff != (self.handoff_variance_hours > 0):
                raise ValueError("late_handoff must match handoff_variance_hours")
        return self


class CaseAssessment(StrictModel):
    primary_issue: PrimaryIssue
    secondary_issues: List[SecondaryIssue] = Field(default_factory=list, max_length=5)
    case_status: Literal["action_required", "no_action"]
    confidence: float = Field(ge=0.0, le=1.0)


class AffectedEntities(StrictModel):
    order_ids: List[EntityId] = Field(default_factory=list, max_length=5)
    item_ids: List[ItemId] = Field(default_factory=list, max_length=5)
    seller_ids: List[EntityId] = Field(default_factory=list, max_length=3)
    payment_ids: List[PaymentId] = Field(default_factory=list, max_length=5)


class CustomerContext(StrictModel):
    customer_unique_id: EntityId
    related_order_ids: List[EntityId] = Field(default_factory=list, max_length=5)


class ProductContext(StrictModel):
    product_ids: List[EntityId] = Field(default_factory=list, max_length=5)
    category_names: List[str] = Field(default_factory=list, max_length=5)


class DeliveryAnalysis(StrictModel):
    delivered_at: Optional[Timestamp] = None
    estimated_delivery_at: Optional[Timestamp] = None
    carrier_handoff_at: Optional[Timestamp] = None
    delivery_variance_hours: Optional[float] = None
    seller_handoff_analysis: List[SellerHandoff] = Field(default_factory=list, max_length=3)
    late_handoff_seller_ids: List[EntityId] = Field(default_factory=list, max_length=3)

    @model_validator(mode="after")
    def validate_late_sellers(self):
        calculated = [row.seller_id for row in self.seller_handoff_analysis if row.late_handoff]
        if self.late_handoff_seller_ids != calculated:
            raise ValueError("late_handoff_seller_ids must match seller_handoff_analysis")
        return self


class PaymentReconciliation(StrictModel):
    currency: Literal["BRL"] = "BRL"
    item_total_brl: Optional[float] = Field(default=None, ge=0)
    freight_total_brl: Optional[float] = Field(default=None, ge=0)
    expected_total_brl: Optional[float] = Field(default=None, ge=0)
    payment_total_brl: Optional[float] = Field(default=None, ge=0)
    difference_brl: Optional[float] = None
    reconciled: Optional[bool] = None
    payment_types: List[str] = Field(default_factory=list)

    _validate_item_total = field_validator(
        "item_total_brl",
        "freight_total_brl",
        "expected_total_brl",
        "payment_total_brl",
        "difference_brl",
    )(_has_at_most_two_decimals)

    @model_validator(mode="after")
    def validate_reconciliation(self):
        item_fields = (self.item_total_brl, self.freight_total_brl, self.expected_total_brl)
        if all(value is None for value in item_fields):
            if self.difference_brl is not None or self.reconciled is not None:
                raise ValueError("orders without items must have null difference/reconciled")
            return self
        if any(value is None for value in item_fields) or self.payment_total_brl is None:
            raise ValueError("payment reconciliation totals must be complete")
        expected = round(self.item_total_brl + self.freight_total_brl, 2)
        difference = round(self.payment_total_brl - expected, 2)
        if self.expected_total_brl != expected or self.difference_brl != difference:
            raise ValueError("payment reconciliation totals are inconsistent")
        if self.reconciled != (abs(difference) <= 0.10):
            raise ValueError("reconciled does not match difference_brl")
        return self


class CauseCode(StrictModel):
    cause_code: CauseCodeValue
    rank: int = Field(ge=1, le=3)


class ResponsibleParty(StrictModel):
    party_type: Literal["seller", "logistics_provider", "platform"]
    party_id: str

    @model_validator(mode="after")
    def validate_party_id(self):
        expected = {
            "platform": "OLIST_PLATFORM",
            "logistics_provider": "LOGISTICS_PROVIDER",
        }
        if self.party_type == "seller":
            if not __import__("re").fullmatch(r"[0-9a-f]{32}", self.party_id):
                raise ValueError("seller party_id must be a seller ID")
        elif self.party_id != expected[self.party_type]:
            raise ValueError("party_id does not match party_type")
        return self


class RootCauseAnalysis(StrictModel):
    ranked_causes: List[CauseCode] = Field(default_factory=list, min_length=1, max_length=3)
    responsible_parties: List[ResponsibleParty] = Field(default_factory=list, max_length=3)


class FinancialResolution(StrictModel):
    currency: Literal["BRL"] = "BRL"
    recommended_refund_brl: float = Field(ge=0)

    _validate_refund = field_validator("recommended_refund_brl")(_has_at_most_two_decimals)


class CaseOutput(StrictModel):
    case_id: CaseId
    case_assessment: CaseAssessment
    affected_entities: AffectedEntities
    customer_context: CustomerContext
    product_context: ProductContext
    delivery_analysis: DeliveryAnalysis
    payment_reconciliation: PaymentReconciliation
    root_cause_analysis: RootCauseAnalysis
    evidence_ids: List[EvidenceId] = Field(default_factory=list, max_length=20)
    financial_resolution: FinancialResolution
    resolution_actions: List[ResolutionAction] = Field(default_factory=list, min_length=1, max_length=5)

    @model_validator(mode="after")
    def validate_resolution(self):
        refund = self.financial_resolution.recommended_refund_brl
        expected_status = "action_required" if refund > 0 else "no_action"
        if self.case_assessment.case_status != expected_status:
            raise ValueError("case_status must match recommended refund")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("evidence_ids must be unique")

        policy_contract = {
            "canceled_order_paid": (
                "ORDER_CANCELED_AFTER_PAYMENT", "issue_full_refund", "platform"
            ),
            "unavailable_order_paid": (
                "ORDER_UNAVAILABLE_AFTER_PAYMENT", "issue_full_refund", "platform"
            ),
            "late_delivery_seller": (
                "SELLER_HANDOFF_AFTER_LIMIT", "refund_freight", "seller"
            ),
            "late_delivery_logistics": (
                "CARRIER_DELIVERED_AFTER_ESTIMATE", "refund_freight",
                "logistics_provider"
            ),
            "valid_split_payment": (
                "MULTIPLE_PAYMENTS_RECONCILED", "explain_valid_split_payment", None
            ),
            "unsupported_late_claim": (
                "DELIVERY_WITHIN_ESTIMATE", "reject_late_refund", None
            ),
        }
        expected_cause, expected_action, expected_party = policy_contract[
            self.case_assessment.primary_issue
        ]
        if self.root_cause_analysis.ranked_causes[0].cause_code != expected_cause:
            raise ValueError("root cause does not match primary_issue")
        if self.resolution_actions[0] != expected_action:
            raise ValueError("primary resolution action does not match primary_issue")
        party_types = [p.party_type for p in self.root_cause_analysis.responsible_parties]
        if expected_party is None and party_types:
            raise ValueError("this primary_issue must not have a responsible party")
        if expected_party is not None and (
            not party_types or any(party != expected_party for party in party_types)
        ):
            raise ValueError("responsible party does not match primary_issue")
        if f"policy:{expected_cause}" not in self.evidence_ids:
            raise ValueError("policy evidence must match root cause")
        return self

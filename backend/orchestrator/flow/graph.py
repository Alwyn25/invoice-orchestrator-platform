from pydantic import BaseModel, Field
from typing import Optional, List
from langgraph.graph import StateGraph, END

class OrchestrationState(BaseModel):
    ingestion_id: str
    ocr_id: Optional[str] = None
    schema_id: Optional[str] = None
    validation_id: Optional[str] = None
    valid: Optional[bool] = None
    requires_human_review: Optional[bool] = None
    report_id: Optional[str] = None
    tally_conversion_id: Optional[str] = None
    zoho_conversion_id: Optional[str] = None
    tally_integration_id: Optional[str] = None
    zoho_integration_id: Optional[str] = None
    status: str = "STARTED"
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

def node_extraction(state: OrchestrationState, clients):
    # In a real implementation, you would call the extraction agent
    state.ocr_id = "OCR-TEST-123"
    return state

def node_mapping(state: OrchestrationState, clients):
    # In a real implementation, you would call the mapping agent
    state.schema_id = "SCHEMA-TEST-123"
    return state

def node_validation(state: OrchestrationState, clients):
    # In a real implementation, you would call the validation agent
    state.validation_id = "VALIDATION-TEST-123"
    state.valid = True  # Or False, or requires_human_review
    state.requires_human_review = False # Or True
    return state

def node_report(state: OrchestrationState, clients):
    # In a real implementation, you would call the report agent
    state.report_id = "REPORT-TEST-123"
    return state

def node_check_review_or_valid(state: OrchestrationState, clients):
    if state.requires_human_review:
        return "human_review_pending"
    elif state.valid:
        return "conversion"
    else:
        return "end"

def node_human_review_pending(state: OrchestrationState, clients):
    state.status = "PENDING_REVIEW"
    return state

def node_conversion(state: OrchestrationState, clients):
    # In a real implementation, you would call the conversion agent
    state.tally_conversion_id = "CONVERSION-TEST-TALLY-123"
    state.zoho_conversion_id = "CONVERSION-TEST-ZOHO-123"
    return state

def node_integration(state: OrchestrationState, clients):
    # In a real implementation, you would call the integration agent
    state.tally_integration_id = "INTEGRATION-TEST-TALLY-123"
    state.zoho_integration_id = "INTEGRATION-TEST-ZOHO-123"
    state.status = "COMPLETED"
    return state

def build_graph(clients):
    graph = StateGraph(OrchestrationState)

    graph.add_node("extraction", lambda state: node_extraction(state, clients))
    graph.add_node("mapping", lambda state: node_mapping(state, clients))
    graph.add_node("validation", lambda state: node_validation(state, clients))
    graph.add_node("report", lambda state: node_report(state, clients))
    graph.add_node("human_review_pending", lambda state: node_human_review_pending(state, clients))
    graph.add_node("conversion", lambda state: node_conversion(state, clients))
    graph.add_node("integration", lambda state: node_integration(state, clients))

    graph.set_entry_point("extraction")
    graph.add_edge("extraction", "mapping")
    graph.add_edge("mapping", "validation")
    graph.add_edge("validation", "report")
    graph.add_conditional_edges(
        "report",
        lambda state: node_check_review_or_valid(state, clients),
        {
            "human_review_pending": "human_review_pending",
            "conversion": "conversion",
            "end": END,
        },
    )
    graph.add_edge("human_review_pending", END)
    graph.add_edge("conversion", "integration")
    graph.add_edge("integration", END)

    return graph.compile()

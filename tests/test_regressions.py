import copy
import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from src.agents.coordinator_agent import CoordinatorAgent
from src.agents.verifier_agent import VerifierAgent
from src.data_loader import INPUT_DIR, OlistDataLoader
from src.llm import DASHSCOPE_MODEL, get_active_model_metadata
from src.schemas import CaseOutput


BASE_DIR = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def datasets():
    return OlistDataLoader().load_all()


@pytest.fixture()
def valid_output():
    with open(BASE_DIR / "output" / "EC_001.json", encoding="utf-8") as handle:
        return json.load(handle)


@pytest.mark.parametrize(
    "mutate",
    [
        lambda data: data["case_assessment"].update(confidence=1.1),
        lambda data: data["case_assessment"].update(case_status="action_required"),
        lambda data: data.update(evidence_ids=["item:not-a-real-id"]),
        lambda data: data["affected_entities"].update(
            item_ids=[data["affected_entities"]["item_ids"][0]] * 6
        ),
    ],
)
def test_strict_schema_rejects_invalid_outputs(valid_output, mutate):
    candidate = copy.deepcopy(valid_output)
    mutate(candidate)
    with pytest.raises(ValidationError):
        CaseOutput.model_validate(candidate)


def test_verifier_rejects_evidence_not_present_in_csv(datasets):
    with pytest.raises(ValueError, match="does not exist"):
        VerifierAgent._validate_evidence_sources(
            ["order:00000000000000000000000000000000"], datasets
        )


def test_customer_message_reaches_policy_prompt(datasets):
    with open(INPUT_DIR / "EC_001.json", encoding="utf-8") as handle:
        case_context = json.load(handle)

    with patch("src.agents.policy_agent.call_llm", return_value="0.88") as mocked_llm:
        result = CoordinatorAgent().analyze(case_context, datasets)

    assert result["is_valid"], result["errors"]
    assert result["output"]["case_assessment"]["confidence"] == 0.88
    assert case_context["customer_request"]["message"] in mocked_llm.call_args.args[0]


def test_metadata_uses_same_fixed_model_as_runtime():
    with patch.dict(os.environ, {}, clear=True):
        fallback = get_active_model_metadata()
        assert fallback["execution_mode"] == "fallback"
        assert fallback["parameter_size"] == "0 (no LLM)"

    with patch.dict(os.environ, {"DASHSCOPE_API_KEY": "test"}, clear=True), patch(
        "src.llm._LAST_EXECUTION_MODE", None
    ), patch("src.llm._PROVIDER_DISABLED", False):
        metadata = get_active_model_metadata()
        assert metadata["model"] == DASHSCOPE_MODEL
        assert metadata["parameter_size"] == "8B"

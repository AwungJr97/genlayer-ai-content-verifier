import json


def configure_mocks(direct_vm):
    direct_vm.mock_web(
        r"https://example\.com/evidence.*",
        {
            "status": 200,
            "body": "Example evidence confirms the submitted claim.",
        },
    )
    direct_vm.mock_llm(
        r".*content quality reviewer.*",
        json.dumps(
            {
                "verdict": "PASS",
                "reason": "The claim is supported by the supplied evidence.",
                "sources": "https://example.com/evidence",
            }
        ),
    )


def test_initial_state(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    assert contract.get_request_count() == 0


def test_empty_content_is_rejected(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    with direct_vm.expect_revert("Text cannot be empty"):
        contract.verify_content("   ")


def test_end_to_end_request_persists_and_can_be_moderated(direct_vm, direct_deploy):
    configure_mocks(direct_vm)
    contract = direct_deploy("contracts/content_verifier.py")

    text = "GenLayer supports decentralized AI consensus. https://example.com/evidence"
    request_id = contract.verify_content(text)

    stored = contract.get_request(request_id)
    assert stored["text"] == text
    assert stored["verdict"] in ("PASS", "REVIEW", "REJECT")
    assert stored["reason"] != ""
    assert stored["sources"] == "https://example.com/evidence"
    assert stored["moderation"] == "PENDING"

    contract.set_moderation(request_id, "APPROVE")
    moderated = contract.get_request(request_id)
    assert moderated["moderation"] == "APPROVE"
    assert moderated["text"] == stored["text"]
    assert moderated["verdict"] == stored["verdict"]


def test_requests_are_stored_separately(direct_vm, direct_deploy):
    configure_mocks(direct_vm)
    contract = direct_deploy("contracts/content_verifier.py")

    first_id = contract.verify_content("First moderation request. https://example.com/evidence")
    second_id = contract.verify_content("Second moderation request. https://example.com/evidence")

    assert first_id != second_id
    assert contract.get_request(first_id)["text"].startswith("First moderation request.")
    assert contract.get_request(second_id)["text"].startswith("Second moderation request.")
    assert contract.get_request_count() == 2

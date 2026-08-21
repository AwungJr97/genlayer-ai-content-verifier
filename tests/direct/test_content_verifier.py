def test_initial_state(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    assert contract.get_request_count() == 0


def test_empty_content_is_rejected(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    with direct_vm.expect_revert("Text cannot be empty"):
        contract.verify_content("   ")


def test_end_to_end_request_persists_and_can_be_moderated(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")

    request_id = contract.verify_content(
        "GenLayer is an intelligent contract platform for decentralized AI consensus."
    )

    stored = contract.get_request(request_id)
    assert stored["text"] == "GenLayer is an intelligent contract platform for decentralized AI consensus."
    assert stored["verdict"] in ("PASS", "REVIEW", "REJECT")
    assert stored["moderation"] == "PENDING"
    assert stored["sources"] != ""

    contract.set_moderation(request_id, "APPROVE")
    moderated = contract.get_request(request_id)
    assert moderated["moderation"] == "APPROVE"
    assert moderated["text"] == stored["text"]
    assert moderated["verdict"] == stored["verdict"]


def test_requests_are_stored_separately(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")

    first_id = contract.verify_content("First moderation request.")
    second_id = contract.verify_content("Second moderation request.")

    assert first_id != second_id
    assert contract.get_request(first_id)["text"] == "First moderation request."
    assert contract.get_request(second_id)["text"] == "Second moderation request."
    assert contract.get_request_count() == 2

def test_initial_state(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    assert contract.get_last_text() == ""
    assert contract.get_last_review() == ""


def test_empty_content_is_rejected(direct_vm, direct_deploy):
    contract = direct_deploy("contracts/content_verifier.py")
    with direct_vm.expect_revert("Text cannot be empty"):
        contract.verify_content("   ")

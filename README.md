# GenLayer AI Content Verifier

A decentralized content moderation application built around a GenLayer Intelligent Contract. Each browser submission becomes its own on-chain moderation request. Validators use GenLayer consensus to review the content, consider relevant factual evidence, and return a structured PASS, REVIEW, or REJECT verdict. A separate moderation control then applies APPROVE, HOLD, or REJECT to that specific request.

## Why GenLayer is central

The core review is not performed only in the browser. `contracts/content_verifier.py` runs `gl.nondet.exec_prompt()` inside `gl.eq_principle.prompt_comparative()`. Validators independently execute the review task and compare the verdict and factual assessment according to an explicit principle. The accepted result is persisted under a unique request ID.

## Request and moderation workflow

```text
Browser UI
   |
   | verify_content(text)
   v
Create unique request ID
   |
   | gl.nondet.exec_prompt()
   v
GenLayer Equivalence Principle
   |
   | validator consensus + relevant source verification
   v
PASS / REVIEW / REJECT stored for that request
   |
   | get_request(request_id)
   v
Moderator reviews evidence and applies:
APPROVE / HOLD / REJECT
   |
   v
Moderation action persisted on the same request
```

## Project structure

```text
contracts/
  content_verifier.py       # Per-request GenLayer Intelligent Contract
frontend/
  index.html                 # Browser entry point
  src/main.js                # GenLayerJS read/write and moderation controls
  src/style.css              # UI
  .env.example               # Contract address configuration
tests/
  direct/test_content_verifier.py
requirements.txt
```

## Run the contract tests

Python 3.12+ is recommended by the GenLayer tooling documentation.

```bash
pip install -r requirements.txt
pytest tests/direct/ -v
```

The direct tests cover input validation, end-to-end request persistence, allowed validator verdicts, per-request isolation, and the moderation action workflow.

## Run the frontend

Node.js 18+ is recommended for the GenLayer frontend tooling.

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Set `VITE_CONTRACT_ADDRESS` to the address of a deployed `ContentVerifier` contract on the GenLayer network you are using. The UI uses `genlayer-js` to:

1. connect to the user's browser wallet,
2. switch the wallet to GenLayer Testnet Bradbury,
3. call `verify_content(text)` as a write transaction,
4. wait for the accepted validator-consensus receipt,
5. read a specific request with `get_request(request_id)`, and
6. apply `APPROVE`, `HOLD`, or `REJECT` to that specific request with `set_moderation()`.

## Evidence-aware review

When factual claims are present, validators are instructed to identify relevant primary or authoritative sources and return them in the structured review. The contract stores the source evidence together with the verdict and reason so the review is not just a globally overwriteable AI opinion.

## Security / scope

This is an educational community project. It does not claim to provide legal, financial, medical, or professional content moderation. Moderation actions are intentionally explicit and request-scoped so a new submission cannot overwrite the result or workflow state of an earlier submission.

## References

- GenLayer Intelligent Contracts: https://docs.genlayer.com/developers/intelligent-contracts/introduction
- Equivalence Principle: https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- GenLayerJS: https://docs.genlayer.com/api-references/genlayer-js

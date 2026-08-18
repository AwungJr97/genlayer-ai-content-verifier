# GenLayer AI Content Verifier

A small decentralized application built around a GenLayer Intelligent Contract. Users submit text from a browser UI, the frontend sends a transaction to GenLayer, and the contract uses an LLM call inside GenLayer's Equivalence Principle to reach validator consensus on a content review.

## Why GenLayer is central

The core decision is not performed only in the browser. `contracts/content_verifier.py` runs `gl.nondet.exec_prompt()` inside `gl.eq_principle.prompt_comparative()`. Validators independently execute the same review task and compare the resulting verdict according to an explicit principle. The accepted result is then written to contract state.

## Project structure

```text
contracts/
  content_verifier.py       # GenLayer Intelligent Contract
frontend/
  index.html                 # Browser entry point
  src/main.js                # GenLayerJS read/write integration
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

The direct tests cover initial contract state and deterministic input validation. The LLM call is intentionally exercised through GenLayer's consensus execution rather than mocked into the application logic.

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
4. wait for the accepted transaction receipt, and
5. read `get_last_review()` from the deployed contract.

## Contract workflow

```text
Browser UI
   |
   | GenLayerJS writeContract()
   v
ContentVerifier.verify_content()
   |
   | gl.nondet.exec_prompt()
   v
GenLayer Equivalence Principle
   |
   | validator consensus
   v
Accepted review stored on-chain
   |
   | GenLayerJS readContract()
   v
Browser UI
```

## Security / scope

This is an educational community project. It does not claim to provide legal, financial, medical, or professional content moderation. The contract stores only the latest submitted text and review result for this simple demonstration.

## References

- GenLayer Intelligent Contracts: https://docs.genlayer.com/developers/intelligent-contracts/introduction
- Equivalence Principle: https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- GenLayerJS: https://docs.genlayer.com/api-references/genlayer-js

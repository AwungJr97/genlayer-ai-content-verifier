import { createClient } from "genlayer-js";
import { testnetBradbury } from "genlayer-js/chains";
import { TransactionStatus } from "genlayer-js/types";
import "./style.css";

const CONTRACT_ADDRESS = import.meta.env.VITE_CONTRACT_ADDRESS;

const app = document.querySelector("#app");
app.innerHTML = `
  <section class="card">
    <p class="eyebrow">GENLAYER DAPP</p>
    <h1>AI Content Verifier</h1>
    <p class="lead">Submit content, let validator consensus review relevant evidence, then apply a real moderation action to that request.</p>
    <textarea id="text" maxlength="2000" placeholder="Enter content to verify..."></textarea>
    <div class="actions">
      <button id="connect">Connect Wallet</button>
      <button id="verify" disabled>Verify Content</button>
      <button id="read" >Read Request</button>
    </div>
    <div class="moderation">
      <input id="requestId" type="number" min="1" placeholder="Request ID" />
      <button id="approve">Approve</button>
      <button id="hold">Hold</button>
      <button id="reject">Reject</button>
    </div>
    <pre id="status">Contract: ${CONTRACT_ADDRESS || "not configured"}</pre>
  </section>
`;

const status = document.querySelector("#status");
const verifyButton = document.querySelector("#verify");
let account;

function readClient() {
  return createClient({ chain: testnetBradbury });
}

function writeClient() {
  return createClient({
    chain: testnetBradbury,
    account,
    provider: window.ethereum,
  });
}

async function connectWallet() {
  if (!window.ethereum) throw new Error("MetaMask or another EIP-1193 wallet is required.");
  const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
  account = accounts[0];
  verifyButton.disabled = !CONTRACT_ADDRESS;
  status.textContent = `Connected: ${account}\nContract: ${CONTRACT_ADDRESS || "not configured"}`;
}

async function getWriteClient() {
  if (!CONTRACT_ADDRESS) throw new Error("Set VITE_CONTRACT_ADDRESS first.");
  if (!account) await connectWallet();
  const client = writeClient();
  await client.connect("testnetBradbury");
  return client;
}

async function verifyContent() {
  const text = document.querySelector("#text").value.trim();
  if (!text) throw new Error("Enter some text first.");

  status.textContent = "Submitting moderation request...";
  const client = await getWriteClient();
  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: "verify_content",
    args: [text],
    value: BigInt(0),
  });

  status.textContent = `Transaction: ${hash}\nWaiting for validator consensus...`;
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
  });
  status.textContent = `Accepted: ${receipt.transactionHash || hash}\nRequest created. Enter its request ID to inspect or moderate it.`;
}

async function readRequest() {
  if (!CONTRACT_ADDRESS) throw new Error("Set VITE_CONTRACT_ADDRESS first.");
  const requestId = Number(document.querySelector("#requestId").value);
  if (!Number.isInteger(requestId) || requestId < 1) throw new Error("Enter a valid request ID.");

  const client = readClient();
  const request = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_request",
    args: [requestId],
  });
  status.textContent = `Request ${requestId}:\n${JSON.stringify(request, null, 2)}`;
}

async function moderate(action) {
  const requestId = Number(document.querySelector("#requestId").value);
  if (!Number.isInteger(requestId) || requestId < 1) throw new Error("Enter a valid request ID.");

  status.textContent = `Submitting ${action} moderation action...`;
  const client = await getWriteClient();
  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: "set_moderation",
    args: [requestId, action],
    value: BigInt(0),
  });

  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
  });
  status.textContent = `${action} accepted for request ${requestId}.\nTransaction: ${receipt.transactionHash || hash}`;
}

document.querySelector("#connect").addEventListener("click", () => connectWallet().catch(showError));
document.querySelector("#verify").addEventListener("click", () => verifyContent().catch(showError));
document.querySelector("#read").addEventListener("click", () => readRequest().catch(showError));
document.querySelector("#approve").addEventListener("click", () => moderate("APPROVE").catch(showError));
document.querySelector("#hold").addEventListener("click", () => moderate("HOLD").catch(showError));
document.querySelector("#reject").addEventListener("click", () => moderate("REJECT").catch(showError));

function showError(error) {
  status.textContent = `Error: ${error?.message || error}`;
}

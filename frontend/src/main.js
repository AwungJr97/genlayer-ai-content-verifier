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
    <p class="lead">Submit text to a GenLayer Intelligent Contract and let validator consensus produce a review.</p>
    <textarea id="text" maxlength="2000" placeholder="Enter content to verify..."></textarea>
    <div class="actions">
      <button id="connect">Connect Wallet</button>
      <button id="verify" disabled>Verify Content</button>
      <button id="refresh">Read Latest Result</button>
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

async function verifyContent() {
  if (!CONTRACT_ADDRESS) throw new Error("Set VITE_CONTRACT_ADDRESS first.");
  if (!account) await connectWallet();
  const text = document.querySelector("#text").value.trim();
  if (!text) throw new Error("Enter some text first.");

  status.textContent = "Submitting transaction...";
  const client = writeClient();
  await client.connect("testnetBradbury");
  const hash = await client.writeContract({
    address: CONTRACT_ADDRESS,
    functionName: "verify_content",
    args: [text],
    value: BigInt(0),
  });

  status.textContent = `Transaction: ${hash}\nWaiting for consensus...`;
  const receipt = await client.waitForTransactionReceipt({
    hash,
    status: TransactionStatus.ACCEPTED,
  });
  status.textContent = `Accepted: ${receipt.transactionHash || hash}\nConsensus completed.`;
}

async function readLatest() {
  if (!CONTRACT_ADDRESS) throw new Error("Set VITE_CONTRACT_ADDRESS first.");
  const client = readClient();
  const review = await client.readContract({
    address: CONTRACT_ADDRESS,
    functionName: "get_last_review",
    args: [],
  });
  status.textContent = `Latest review:\n${review || "No review stored yet."}`;
}

document.querySelector("#connect").addEventListener("click", () => connectWallet().catch(showError));
document.querySelector("#verify").addEventListener("click", () => verifyContent().catch(showError));
document.querySelector("#refresh").addEventListener("click", () => readLatest().catch(showError));

function showError(error) {
  status.textContent = `Error: ${error?.message || error}`;
}

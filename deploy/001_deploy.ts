import { readFileSync } from "fs";
import path from "path";
import {
  DecodedDeployData,
  GenLayerChain,
  TransactionStatus,
} from "genlayer-js/types";
import { testnetBradbury } from "genlayer-js/chains";

export default async function main(client: any) {
  const filePath = path.resolve(process.cwd(), "contracts/content_verifier.py");
  const code = new Uint8Array(readFileSync(filePath));

  await client.initializeConsensusSmartContract();

  const deployTransaction = await client.deployContract({
    code,
    args: [],
  });

  const receipt = await client.waitForTransactionReceipt({
    hash: deployTransaction,
    status: TransactionStatus.FINALIZED,
    retries: 100,
    interval: 5000,
  });

  const address =
    (client.chain as GenLayerChain).id !== testnetBradbury.id
      ? receipt.data.contract_address
      : (receipt.txDataDecoded as DecodedDeployData)?.contractAddress;

  console.log(`ContentVerifier deployed at: ${address}`);
  return address;
}

// MUTATING opt-in smoke: deploys a NEW gasless StudioNet contract.
// Ephemeral signing keys remain in memory and are never printed or saved.
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
import {createClient,createAccount} from 'genlayer-js';
import {studionet} from 'genlayer-js/chains';

const clients=Array.from({length:5},()=>createClient({chain:studionet,account:createAccount()}));
const root=resolve(import.meta.dirname,'..');
const code=readFileSync(resolve(root,'contracts/counterpart.py'),'utf8');
async function finalized(client,hash,label){
  const tx=await client.waitForTransactionReceipt({hash,status:'FINALIZED',interval:5000,retries:90});
  assert.equal(tx.status_name??tx.statusName,'FINALIZED');
  assert.equal(tx.consensus_data?.leader_receipt?.[0]?.execution_result??tx.txExecutionResultName,'SUCCESS');
  console.log(`${label}: ${hash}`);
  return tx;
}
const deployHash=await clients[0].deployContract({code,args:[]});
const deployment=await finalized(clients[0],deployHash,'deploy');
const address=deployment.recipient;
assert.equal(await clients[0].getContractCode(address),code);
const read=()=>clients[0].readContract({address,functionName:'get_batch',args:[1],jsonSafeReturn:true});
async function write(idx,method,args){
  const hash=await clients[idx].writeContract({address,functionName:method,args,value:0n});
  return finalized(clients[idx],hash,method);
}
await write(0,'open_batch',['Translation and copyediting exchange',600,3600]);
const entries=[
 ['demand','Translate a public English API tutorial into Indonesian.',''],
 ['demand','Copyedit a public English API tutorial for grammar and clarity, keeping it in English.',''],
 ['supply','English-to-Indonesian translation and English grammar/clarity copyediting of API tutorials.','Public API tutorials only.'],
 ['supply','Translate English API tutorials into Indonesian. I do not offer English copyediting.','Public API tutorials only.']
];
for(let i=0;i<4;i++) await write(i+1,'join',[1,...entries[i]]);
const closesAt=(await read()).closes_at;
while(Date.now()/1000<closesAt+2){
  console.log('Waiting for immutable collection deadline');
  await new Promise(resolve=>setTimeout(resolve,Math.min(30000,(closesAt+2-Date.now()/1000)*1000)));
}
await write(0,'clear',[1]);
const batch=await read();
assert.deepEqual(batch.matches.map(m=>[m.demand_id,m.supply_id]),[[0,1],[1,0]]);
for(let i=0;i<batch.matches.length;i++){
  const m=batch.matches[i];
  await write(m.demand_id+1,'confirm',[1,i,batch.input_digest]);
  await write(m.supply_id+3,'confirm',[1,i,batch.input_digest]);
}
assert((await read()).matches.every(m=>m.status==='AGREED'));
console.log(`Smoke passed on fresh deployment ${address}. Demonstration keys were not persisted.`);

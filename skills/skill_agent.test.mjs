import test from 'node:test';
import assert from 'node:assert/strict';
import {callGeminiWithRetry,syncToDriveWebhook,redact} from './skill_agent.mjs';
const env={GEMINI_API_KEY:'synthetic-test-key',BRIDGE_SECRET:'synthetic-bridge-key',DRIVE_WEBHOOK_URL:'https://script.google.com/macros/s/test/exec'};
const ok=()=>({ok:true,status:200,json:async()=>({candidates:[{content:{parts:[{text:'summary'}]}}]})});
test('503 bounded backoff then success; key stays out of URL',async()=>{
 let calls=0; const waits=[];
 const r=await callGeminiWithRetry('fixture',{env,models:['m'],sleep:async n=>waits.push(n),fetch:async(url,opt)=>{
  assert.ok(!url.includes(env.GEMINI_API_KEY));assert.equal(opt.headers['x-goog-api-key'],env.GEMINI_API_KEY);
  return ++calls<3?{ok:false,status:503}:ok();
 }});
 assert.equal(r.text,'summary');assert.equal(calls,3);assert.deepEqual(waits,[5000,15000]);
});
test('404 switches models without retrying unavailable model',async()=>{
 const urls=[]; const r=await callGeminiWithRetry('fixture',{env,models:['old','new'],sleep:async()=>assert.fail(),fetch:async u=>{urls.push(u);return urls.length===1?{ok:false,status:404}:ok();}});
 assert.equal(r.model,'new');assert.equal(urls.length,2);
});
test('429 exhaustion is bounded and does not fabricate output',async()=>{
 let calls=0;const r=await callGeminiWithRetry('fixture',{env,models:['m'],sleep:async()=>{},fetch:async()=>{calls++;return{ok:false,status:429};}});
 assert.equal(r.ok,false);assert.equal(calls,3);assert.equal(r.text,undefined);
});
test('HTTP200 unauthorized webhook is failure; ok:true succeeds',async()=>{
 await assert.rejects(syncToDriveWebhook('MSG_test.md','fixture',{env,fetch:async()=>({ok:true,status:200,json:async()=>({ok:false,error:'unauthorized'})})}),/rejected/);
 const r=await syncToDriveWebhook('MSG_test.md','fixture',{env,fetch:async()=>({ok:true,status:200,json:async()=>({ok:true,status:'SYNCED_TO_DRIVE'})})});
 assert.equal(r.ok,true);
});
test('non-JSON webhook and missing configuration fail closed; diagnostics redact secrets',async()=>{
 await assert.rejects(syncToDriveWebhook('MSG_test.md','fixture',{env,fetch:async()=>({json:async()=>{throw Error('html');}})}),/JSON/);
 await assert.rejects(syncToDriveWebhook('MSG_test.md','fixture',{env:{}}),/Missing/);
 for(const value of Object.values(env))assert.ok(!redact(Object.values(env).join(' '),env).includes(value));
});
import {discoverModels,MODELS} from './skill_agent.mjs';
test('MODELS không còn model đã tắt gemini-2.0-flash',()=>{assert.ok(!MODELS.includes('gemini-2.0-flash'));assert.equal(MODELS[0],'gemini-3.8-flash');});
test('discoverModels lọc theo danh sách khả dụng, key chỉ ở header',async()=>{
 const r=await discoverModels(['a','b','c'],{env,fetch:async(u,o)=>{assert.ok(!u.includes(env.GEMINI_API_KEY));assert.equal(o.headers['x-goog-api-key'],env.GEMINI_API_KEY);
  return{ok:true,json:async()=>({models:[{name:'models/b',supportedGenerationMethods:['generateContent']},{name:'models/a',supportedGenerationMethods:['embedContent']}]})}}});
 assert.deepEqual(r,['b']);
});
test('discoverModels lỗi API thì dùng danh sách tĩnh',async()=>{
 assert.deepEqual(await discoverModels(['x'],{env,fetch:async()=>({ok:false,status:500})}),['x']);
});

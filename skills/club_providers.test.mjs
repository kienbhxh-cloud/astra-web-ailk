import test from 'node:test';
import assert from 'node:assert/strict';
import {createClubProviders} from './club_providers.mjs';
const ds=(content='OK')=>({ok:true,status:200,json:async()=>({model:'deepseek-chat',choices:[{message:{content}}]})});
const or=(content='OK')=>({ok:true,status:200,json:async()=>({model:'deepseek/deepseek-r1:free',choices:[{message:{content}}]})});
const gm=(content='OK')=>({ok:true,status:200,json:async()=>({model:'gemini-2.5-flash',candidates:[{content:{parts:[{text:content}]}}]})});
function contract(r){for(const k of ['ok','intended_provider','actual_provider','model','status','error','latency_ms','trace'])assert.ok(Object.hasOwn(r,k),k);assert.ok(Array.isArray(r.trace));}
test('a: missing DeepSeek key logged NO_KEY without pretending DeepSeek connection',async()=>{
 const p=createClubProviders({env:{GEMINI_API_KEY:'synthetic-g',CLUB_MODELS:'gemini-2.5-flash'},request:async()=>gm()});
 const r=await p.askDeepSeekOrFallback('audit','topic');contract(r);
 assert.equal(r.ok,true);assert.equal(r.actual_provider,'Gemini');assert.equal(r.intended_provider,'DeepSeek');
 assert.ok(r.trace.some(e=>e.provider==='DeepSeek'&&e.event==='SKIPPED: NO_KEY'));
});
test('b: DeepSeek 429 then OpenRouter 200, actual provider matches successful endpoint',async()=>{
 const seen=[];const p=createClubProviders({env:{DEEPSEEK_API_KEY:'SECRET_A',OPENROUTER_API_KEY:'SECRET_B'},wait:async()=>{},request:async (url)=>{seen.push(url);return url.includes('api.deepseek.com')?{ok:false,status:429}:or();}});
 const r=await p.askDeepSeekOrFallback('audit','topic');contract(r);
 assert.equal(r.ok,true);assert.equal(r.actual_provider,'OpenRouter-DeepSeek');assert.equal(r.model,'deepseek/deepseek-r1:free');
 assert.ok(r.trace.some(e=>e.provider==='DeepSeek'&&e.event==='HTTP 429'));assert.ok(r.trace.some(e=>e.provider==='OpenRouter-DeepSeek'&&e.event==='HTTP 200'));
 assert.ok(!JSON.stringify(r).includes('SECRET_A'));assert.ok(!JSON.stringify(r).includes('SECRET_B'));
 assert.equal(seen.length,3);
});
test('c: all candidates unavailable -> ok false and no invented provider',async()=>{
 const p=createClubProviders({env:{DEEPSEEK_API_KEY:'key1',OPENROUTER_API_KEY:'key2',GEMINI_API_KEY:'key3',CLUB_MODELS:'gemini-2.5-flash'},wait:async()=>{},request:async()=>({ok:false,status:503})});
 const r=await p.askDeepSeekOrFallback('audit','topic');contract(r);
 assert.equal(r.ok,false);assert.equal(r.actual_provider,null);assert.equal(r.error,'ALL_PROVIDERS_UNAVAILABLE');
 assert.ok(r.trace.every(e=>e.event==='HTTP 503'));
});
test('HTTP 200 empty answer cannot return success',async()=>{
 const p=createClubProviders({env:{GEMINI_API_KEY:'g',CLUB_MODELS:'gemini-2.5-flash'},request:async()=>gm('')});
 const r=await p.askGemini('role','topic');assert.equal(r.ok,false);assert.ok(r.trace.some(e=>e.event==='EMPTY_OR_INVALID_CONTENT'));
});

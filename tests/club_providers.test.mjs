import test from 'node:test';
import assert from 'node:assert/strict';
import {createClubProviders} from '../skills/club_providers.mjs';

const json=(data,status=200)=>({status,ok:status>=200&&status<300,json:async()=>data});
test('DeepSeek configured: actual provider from successful endpoint, never inferred from role name',async()=>{
 const calls=[];
 const providers=createClubProviders({
  env:{DEEPSEEK_API_KEY:'FAKE_TEST_KEY',GEMINI_API_KEY:'FAKE_TEST_KEY',CLUB_MODELS:'gemini-2.5-flash'},
  request:async (url,opts)=>{calls.push({url,opts});return json({model:'deepseek-chat',choices:[{message:{content:'valid deepseek test'}}]});},
  wait:async()=>{}
 });
 const out=await providers.askDeepSeekOrFallback('auditor','test');
 assert.equal(out.intended_provider,'DeepSeek');
 assert.equal(out.actual_provider,'DeepSeek');
 assert.equal(out.provider,'DeepSeek');
 assert.equal(out.http_status,200);
 assert.equal(out.provider_evidence,'HTTP_SUCCESS_FROM_CONFIGURED_ENDPOINT');
 assert.equal(out.model,'deepseek-chat');
 assert.equal(calls.length,1);
});
test('fallback: actual Gemini response must be labeled Gemini with intended DeepSeek and fallback reason',async()=>{
 const paths=[];
 const providers=createClubProviders({
  env:{DEEPSEEK_API_KEY:'FAKE_TEST_KEY',GEMINI_API_KEY:'FAKE_TEST_KEY',CLUB_MODELS:'gemini-2.5-flash'},
  request:async(url)=>{paths.push(url);if(url.includes('api.deepseek.com'))return json({error:'unavailable'},503);return json({model:'gemini-2.5-flash',candidates:[{content:{parts:[{text:'gemini fallback test'}]}}]});},
  wait:async()=>{}
 });
 const out=await providers.askDeepSeekOrFallback('auditor','test');
 assert.equal(out.intended_provider,'DeepSeek');
 assert.equal(out.actual_provider,'Gemini');
 assert.equal(out.provider,'Gemini');
 assert.equal(out.model,'gemini-2.5-flash');
 assert.equal(out.http_status,200);
 assert.ok(out.fallback);
 assert.ok(paths.some(p=>p.includes('deepseek')));
 assert.ok(paths.some(p=>p.includes('generativelanguage')));
});
test('unconfigured DeepSeek: Gemini fallback cannot claim DeepSeek connected',async()=>{
 const providers=createClubProviders({
  env:{GEMINI_API_KEY:'FAKE_TEST_KEY',CLUB_MODELS:'gemini-2.5-flash'},
  request:async()=>json({candidates:[{content:{parts:[{text:'ok'}]}}]}),
  wait:async()=>{}
 });
 const out=await providers.askDeepSeekOrFallback('auditor','topic');
 assert.equal(out.provider,'Gemini');assert.equal(out.actual_provider,'Gemini');
 assert.equal(out.intended_provider,'DeepSeek');assert.ok(out.fallback);
});

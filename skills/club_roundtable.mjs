#!/usr/bin/env node
// ASTRA Roundtable v1.2: deterministic fixture, explicit live mode and pending skills.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createClubProviders} from './club_providers.mjs';

const args=process.argv.slice(2), value=key=>{const i=args.indexOf(key);return i>=0?args[i+1]||'':'';};
const fixture=args.includes('--fixture'), live=args.includes('--live');
if(fixture===live){console.error('Choose exactly one mode --fixture or --live');process.exit(2);}
const topic=value('--topic')||process.env.CLUB_TOPIC_FILE||'';
if(!/^09_HOP_THU\/[A-Za-z0-9_.-]+\.md$/.test(topic)||topic.includes('..')||topic.endsWith('_CLUB_MINUTES.md')){console.error('Invalid --topic');process.exit(2);}
if(!fs.existsSync(topic)){console.error('Missing topic');process.exit(2);}
const body=fs.readFileSync(topic,'utf8');
if(body.length>12000){console.error('BLOCKED: TOPIC_OVER_12000_CHARS');process.exit(2);}
const first20=body.split(/\r?\n/).slice(0,20).join('\n');
if(!/\[CLUB:ROUNDTABLE\]/i.test(first20)){console.log('SKIP: tag must occur in first 20 lines');process.exit(0);}
const digest=crypto.createHash('sha256').update(body).digest('hex');
const base=path.basename(topic,'.md'),minutes=`09_HOP_THU/${base}_CLUB_MINUTES.md`;
if(fs.existsSync(minutes)){console.log('SKIP_EXISTING: '+minutes);process.exit(0);}
const provider=createClubProviders();
const samples={
 A:'Đề nghị gắn Task ID, trạng thái và bằng chứng sau mỗi hành động để điều phối công việc minh bạch.',
 B:'Rủi ro: ghi sai ACK, giả định kết quả đã được reviewer duyệt hoặc tiết lộ dữ liệu công khai; cần chống trùng.',
 CA:'Lỗ hổng đối với B: quy trình quá chậm vì kiểm duyệt. Bản vá: có chế độ fixture gắn nhãn và cách ly kết quả.',
 CB:'Lỗ hổng đối với A: thiếu xác minh nguồn ACK. Bản vá: đối chiếu dispatch_id và log xác nhận.',
 S:'SCORE: 90\nSKILL_CODE: EVIDENCE_GATE\nSUMMARY: Dùng mã tác vụ và log riêng.\nSKILL_RULE: Không nghiệm thu kết quả khi chưa có kiểm chứng độc lập.'
};
async function ask(kind,role,prompt){
 if(fixture)return {ok:true,intended_provider:'FIXTURE',actual_provider:'FIXTURE',model:'FIXTURE_NO_LLM',status:200,error:null,latency_ms:0,trace:[{event:'FIXTURE_NO_API'}],text:samples[kind]};
 return kind==='B'||kind==='CB'?provider.askDeepSeekOrFallback(role,prompt):provider.askGemini(role,prompt);
}
const [a,b]=await Promise.all([ask('A','Architect',body),ask('B','Auditor',body)]);
function required(result,stage){if(!result.ok||!result.text?.trim())throw Error('MODEL_FAILED_'+stage+': '+(result.error||'EMPTY'));
 return result;}
required(a,'A');required(b,'B');
const ca=required(await ask('CA','Critic A','Review B: '+b.text),'CA');
const cb=required(await ask('CB','Critic B','Review A: '+a.text),'CB');
const s=required(await ask('S','Synthesis','Topic: '+body+'\nA: '+a.text+'\nB: '+b.text+'\nCritiques: '+ca.text+'\n'+cb.text+'\nOutput SCORE: <integer>, SKILL_CODE:, SUMMARY:, SKILL_RULE:'),'S');
const match=s.text.match(/^SCORE:\s*(100|[1-9]?\d)\s*$/mi);
const score=match?Number(match[1]):null;
const code=(s.text.match(/^SKILL_CODE:\s*([A-Z][A-Z0-9_-]{2,60})\s*$/mi)||[])[1];
const eligible=score!==null&&score>=85&&code&&/^SUMMARY:\s*\S/im.test(s.text)&&/^SKILL_RULE:\s*\S/im.test(s.text);
const resultStatus=score===null?'REJECTED_NO_SCORE':eligible?'REVIEW_PENDING':'REJECTED_BELOW_THRESHOLD';
const mode=fixture?'FIXTURE_SIMULATION':'LIVE_MULTI_PROVIDER_API';
const rounds=[a,b,ca,cb,s];
const fmt=r=>[r.intended_provider,r.actual_provider||'NONE',r.model||'NONE',r.status,r.latency_ms].join('/');
const text=['# ASTRA Club Roundtable v1.2','','- Source: '+topic,'- SHA256: '+digest,'- Mode: '+mode,
 '- Status: '+resultStatus,'- score: '+(score===null?'null':`[SELF-REPORTED] ${score}/100`),'- reviewer_id: null','- review_timestamp: null',
 '- Provider actual response trail: '+rounds.map(fmt).join(' | '),'',
 '## ROUND 1A',a.text,'','## ROUND 1B',b.text,'',
 '## ROUND 2A',ca.text,'','## ROUND 2B',cb.text,'',
 '## ROUND 3',s.text,''];
let pending='';
if(eligible){
 pending='10_SKILLS/_pending/AUTO_'+code.replace(/^AUTO_/,'')+'_'+digest.slice(0,8)+'.md';
 fs.mkdirSync(path.dirname(pending),{recursive:true});
 const skill=['# Candidate club skill: '+code,'',`> [SELF-REPORTED] score=${score} · status=REVIEW_PENDING · reviewer_id=null · review_timestamp=null`,
 '- source: '+topic,'- sha256: '+digest,'- mode: '+mode,'- NOTE: Do not load into any agent until REVIEW_ACCEPT with named reviewer.','','## Proposed skill',s.text,''].join('\n');
 fs.writeFileSync(pending,skill,{flag:'wx'});
 text.push('- Pending skill: '+pending);
}
fs.mkdirSync(path.dirname(minutes),{recursive:true});
fs.writeFileSync(minutes,text.join('\n'),{flag:'wx'});
if(fs.existsSync('AI_FEED.md'))fs.appendFileSync('AI_FEED.md','\n### [CLUB:ROUNDTABLE] '+base+'\nMode: '+mode+'; score: '+(score===null?'null':`[SELF-REPORTED] ${score}`)+'; status='+resultStatus+'; reviewer_id=null; review_timestamp=null; minutes='+minutes+'; pending_skill='+(pending||'NONE')+'\n');
console.log(JSON.stringify({ok:true,source:topic,mode,score,status:resultStatus,minutes,pending_skill:pending||null}));

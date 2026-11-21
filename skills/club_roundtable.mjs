#!/usr/bin/env node
// ASTRA Club Roundtable v1.1. Runs fixture only with explicit --fixture.
// LIVE requires explicit mode and configured API secrets; no real calls in fixture. Every round labels provider/mode.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {createClubProviders} from './club_providers.mjs';

const root = process.cwd(), args=process.argv.slice(2);
const getArg=k=>{const i=args.indexOf(k); return i<0?'':args[i+1]||'';};
const fixture=args.includes('--fixture');
const live=args.includes('--live');
if(fixture===live) {console.error('CHOOSE exactly one: --fixture or --live');process.exit(2);}
const relative=getArg('--topic')||process.env.CLUB_TOPIC_FILE||'';
if(!/^09_HOP_THU\/[a-zA-Z0-9_.-]+\.md$/.test(relative)||relative.includes('..')||relative.includes('_CLUB_MINUTES')){console.error('Invalid --topic (09_HOP_THU/*.md required)');process.exit(2);}
const topicPath=path.join(root,relative);
if(!fs.existsSync(topicPath)){console.error('Topic file missing:',relative);process.exit(2);}
const content=fs.readFileSync(topicPath,'utf8');
if(!/\[CLUB:(?:ROUNDTABLE|ARENA|THAO_LUAN)\]/i.test(content)){console.log('SKIP: no club marker');process.exit(0);}
if(content.length>12000){console.error('Topic too long');process.exit(2);}
const digest=crypto.createHash('sha256').update(content).digest('hex');
const base=path.basename(relative,'.md'), minutesRel='09_HOP_THU/'+base+'_CLUB_MINUTES.md';
const minutesAbs=path.join(root,minutesRel);
if(fs.existsSync(minutesAbs)){console.log('SKIP_EXISTING:',minutesRel);process.exit(0);}
const providers=createClubProviders();
async function ask(role,prompt,number){
 if(fixture){
  const answers={
   A:'Đề nghị ghi trạng thái FACT / UNVERIFIED cho từng bước, tạo mã chủ đề và nhật ký kiểm thử. Mọi worker phải có nguồn kiểm chứng, không đồng nhất một vai trò với một AI kết nối thực.',
   B:'Rủi ro: dữ liệu công khai lộ thông tin riêng, phát sinh phí API, score tự đánh giá và thao tác ghi trùng. Chặn ghi trùng theo SHA, giới hạn chi phí và yêu cầu review trước khi dùng skill.',
   CA:'Lỗ hổng giải pháp B: thiếu điểm dừng khi thiếu chứng cứ. Bản vá: phát trạng thái BLOCKED, khóa phát hành và ghi đường dẫn kiểm tra.',
   CB:'Lỗ hổng giải pháp A: bảo mật có thể chặn cả demo. Bản vá: chạy fixture trong môi trường cô lập, gắn nhãn DEMO và cho chủ dự án nghiệm thu thủ công.',
   S:'SCORE: 90\nSKILL_CODE: CLUB_EVIDENCE_GATE\nSUMMARY: Chỉ vận hành đối với chủ đề được gắn thẻ; lưu SHA nguồn; tách DEMO và LIVE; chặn chạy trùng; yêu cầu người rà soát trước khi coi skill có hiệu lực.\nSKILL_RULE: Trước khi thông báo hoàn tất, xác định nguồn thật, môi trường, mã tác vụ, log và kết quả hậu kiểm. Nếu thiếu bằng chứng phải ghi UNVERIFIED.'
  };
  return {provider:'Fixture',model:'FIXTURE_NO_LLM',text:answers[number]};
 }
 return (number==='B'||number==='CB')?providers.askDeepSeekOrFallback(role,prompt):providers.askGemini(role,prompt);
}
function safe(s){return String(s).replace(/[\u0000-\u0008\u000b-\u001f]/g,'').slice(0,12000);}
const roleA='Kien truc su sang tao',roleB='Kiem toan vien khat khe';
const [a,b]=await Promise.all([
 ask(roleA,content,'A'),ask(roleB,content,'B')
]);
const ca=await ask('Phan bien A ve B','De xuat B:\n'+b.text+'\nHay neu it nhat 1 lo hong va 1 ban va cu the.','CA');
const cb=await ask('Phan bien B ve A','De xuat A:\n'+a.text+'\nHay neu it nhat 1 lo hong va 1 ban va cu the.','CB');
const synthesis=await ask('Tong hop va cham diem','TOPIC:\n'+content+'\nA:\n'+a.text+'\nB:\n'+b.text+'\nCRITIQUE A:\n'+ca.text+'\nCRITIQUE B:\n'+cb.text+'\nOutput SCORE: <0-100>, SKILL_CODE: <ASCII>, SUMMARY:, SKILL_RULE:.','S');
const match=synthesis.text.match(/^SCORE:\s*(100|[1-9]?\d)\s*$/mi);
const score=match?Number(match[1]):null;
const code=(synthesis.text.match(/^SKILL_CODE:\s*([A-Z0-9_-]{3,60})\s*$/mi)||[])[1];
const hasRule=/^SKILL_RULE:\s*\S/im.test(synthesis.text),hasSummary=/^SUMMARY:\s*\S/im.test(synthesis.text);
const eligible=score!==null&&score>=85&&code&&hasRule&&hasSummary&&ca.text.length>=40&&cb.text.length>=40;
const mode=fixture?'FIXTURE_SIMULATION':'LIVE_MULTI_PROVIDER_API';
let skillRel='';
const lines=['# ASTRA CLUB ROUNDTABLE - Three round minutes','',
 '- Source: '+relative,'- SHA256: '+digest,'- Execution: '+mode,'- Models: '+[a,b,ca,cb,synthesis].map(r=>r.provider+'/'+r.model+(r.fallback?' (Gemini fallback)':'')).join(', '), '- Provider provenance (intended/actual/status): '+[a,b,ca,cb,synthesis].map(r=>(r.intended_provider||r.provider)+'/'+(r.actual_provider||r.provider)+'/'+(r.http_status||'FIXTURE')).join(', '),
 '- Quality score: [SELF-REPORTED] '+(score===null?'UNPARSEABLE':score+'/100 (model self-assessment, not verified)'),
 '- Review: PENDING HUMAN OR CROSS-FAMILY VALIDATION', '- reviewer_id: UNASSIGNED', '- review_timestamp: NOT_REVIEWED','',
 '## ROUND 1A - Independent architecture',safe(a.text),'',
 '## ROUND 1B - Independent audit',safe(b.text),'',
 '## ROUND 2A - Critique of B',safe(ca.text),'',
 '## ROUND 2B - Critique of A',safe(cb.text),'',
 '## ROUND 3 - Synthesis & proposed skill',safe(synthesis.text),''];
if(eligible){
 const safeCode=code.replace(/^AUTO_/,'');
 skillRel='10_SKILLS/AUTO_'+safeCode+'_'+digest.slice(0,8)+'.md';
 const skill=['# AUTO-PROPOSED ASTRA SKILL: '+safeCode,'',
  '- Status: '+(fixture?'FIXTURE_ONLY_NOT_VALIDATED':'DRAFT_REVIEW_REQUIRED'),
  '- Source: '+relative,'- Topic SHA256: '+digest,'- Model-score: [SELF-REPORTED] '+score+'/100 (not external acceptance)', '- reviewer_id: UNASSIGNED','- review_timestamp: NOT_REVIEWED',
  '- DO NOT blindly load as a system-level skill until independently reviewed.','','## Proposed rule',safe(synthesis.text),''].join('\n');
 fs.mkdirSync(path.dirname(path.join(root,skillRel)),{recursive:true});
 fs.writeFileSync(path.join(root,skillRel),skill,{flag:'wx'});
 lines.push('- Proposed skill: '+skillRel+' (NOT auto-approved)');
}else{lines.push('- Proposed skill: none. Threshold or schema was not met.');}
fs.mkdirSync(path.dirname(minutesAbs),{recursive:true});
fs.writeFileSync(minutesAbs,lines.join('\n'),{flag:'wx'});
const feedFile=path.join(root,'AI_FEED.md');
if(fs.existsSync(feedFile)){
 fs.appendFileSync(feedFile,'\n### [CLUB:ROUNDTABLE] '+base+'\nRoundtable '+mode+', topic sha256='+digest+', score=[SELF-REPORTED] '+(score??'N/A')+'; reviewer_id=UNASSIGNED; review_timestamp=NOT_REVIEWED; minutes: '+minutesRel+'; skill: '+(skillRel||'NONE')+'; review pending.\n');
}
if(live&&process.env.DRIVE_WEBHOOK_URL){
 const url=process.env.DRIVE_WEBHOOK_URL;
 if(!url.startsWith('https://')||!process.env.BRIDGE_SECRET)throw Error('WEBHOOK_CONFIGURATION_INVALID - minutes saved locally');
 const rsp=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret:process.env.BRIDGE_SECRET,fileName:path.basename(minutesRel),content:lines.join('\n')})});
 const body=await rsp.json().catch(()=>({}));
 if(!rsp.ok||body.ok!==true)throw Error('DRIVE_SYNC_FAILED - local minutes saved, no claim of sync');
}
console.log(JSON.stringify({status:'MINUTES_CREATED',mode,source:relative,sha256:digest,score,skill:skillRel||null,minutes:minutesRel,review:'PENDING'}));


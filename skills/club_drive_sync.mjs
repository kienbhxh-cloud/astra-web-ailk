// ASTRA Club v1.2. This script alone receives Drive webhook secrets.
import fs from 'node:fs';
import path from 'node:path';
const file=process.argv[process.argv.indexOf('--minutes')+1]||'';
if(!/^09_HOP_THU\/[A-Za-z0-9_.-]+_CLUB_MINUTES\.md$/.test(file)||file.includes('..'))throw Error('INVALID_MINUTES_FILE');
if(!fs.existsSync(file))throw Error('MISSING_MINUTES_FILE');
const url=process.env.DRIVE_WEBHOOK_URL||'',secret=process.env.BRIDGE_SECRET||'';
if(!url&&!secret){console.log('DRIVE_SYNC_SKIPPED_NO_CONFIG');process.exit(0);}
if(!url||!secret)throw Error('DRIVE_SYNC_CONFIG_INCOMPLETE');
const target=new URL(url);
if(target.protocol!=='https:'||target.hostname!=='script.google.com'||!target.pathname.endsWith('/exec'))throw Error('DRIVE_SYNC_URL_NOT_ALLOWLISTED');
const rsp=await fetch(target.href,{method:'POST',redirect:'follow',headers:{'Content-Type':'application/json'},body:JSON.stringify({secret,fileName:path.basename(file),content:fs.readFileSync(file,'utf8')}),signal:AbortSignal.timeout(30000)});
const data=await rsp.json().catch(()=>null);
if(!rsp.ok||data?.ok!==true)throw Error('DRIVE_SYNC_REJECTED');
console.log('DRIVE_SYNC_CONFIRMED: '+path.basename(file));

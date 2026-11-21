import fs from 'node:fs';
import path from 'node:path';
export function loadApprovedSkill(skillName,{root=process.cwd()}={}){
 if(!/^[A-Z0-9_-]{2,80}$/.test(skillName))throw Error('INVALID_SKILL_NAME');
 const dir=path.join(root,'10_SKILLS'),target=path.join(dir,skillName+'.md');
 if(!fs.existsSync(target))throw Error('UNKNOWN_SKILL');
 const realDir=fs.realpathSync(dir),realTarget=fs.realpathSync(target);
 if(path.dirname(realTarget)!==realDir)throw Error('SKILL_OUTSIDE_APPROVED_DIRECTORY');
 const source=fs.readFileSync(realTarget,'utf8');
 const meta={};for(const line of source.split(/\r?\n/).slice(0,24)){
  const m=line.match(/^\s*(?:>\s*)?(?:-\s*)?(status|reviewer_id)\s*[:=]\s*([A-Za-z0-9_.-]+)\s*$/i);
  if(m)meta[m[1].toLowerCase()]=m[2];
 }
 if(meta.status!=='REVIEW_ACCEPT'||!meta.reviewer_id||/^(?:null|none|unassigned|pending)$/i.test(meta.reviewer_id))throw Error('SKILL_NOT_REVIEW_ACCEPT');
 return {content:source,reviewer_id:meta.reviewer_id,status:meta.status,path:target};
}

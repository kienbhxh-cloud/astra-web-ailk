/**
 * ASTRA Bridge Drive <-> GitHub (bản đã siết chặt bởi Claude, dựa trên mã của Gemini MSG_20261118-1532).
 * Khác bản gốc: (1) BẮT BUỘC secret ngẫu nhiên, không có mặc định; (2) chỉ đồng bộ tệp tên MSG_* / ASTRA_DRIVER_*
 * (không đẩy mọi tệp trong thư mục lên kho CÔNG KHAI); (3) giới hạn dung lượng; (4) tên tệp được làm sạch.
 * Cách dùng: dán vào script.google.com, đặt Script Properties: GITHUB_TOKEN (fine-grained, chỉ kho astra-web-ailk,
 * Contents: Read and write), BRIDGE_SECRET (chuỗi ngẫu nhiên dài), rồi chạy setupBridge() 1 lần.
 */
const CONFIG = { GITHUB_OWNER:'kienbhxh-cloud', GITHUB_REPO:'astra-web-ailk', GITHUB_BRANCH:'main', GITHUB_FOLDER:'09_HOP_THU', DRIVE_FOLDER_NAME:'09_HOP_THU', MAX_BYTES:200000 };
const NAME_OK = /^(MSG_|ASTRA_DRIVER_)[A-Za-z0-9._\-]{3,150}$/;

function props_(){ return PropertiesService.getScriptProperties(); }
function setupBridge(){
  const p = props_();
  if(!p.getProperty('GITHUB_TOKEN')) throw new Error('Hãy đặt Script Property GITHUB_TOKEN trong Project Settings trước.');
  if(!p.getProperty('BRIDGE_SECRET') || p.getProperty('BRIDGE_SECRET').length < 16) throw new Error('Đặt Script Property BRIDGE_SECRET (>=16 ký tự ngẫu nhiên).');
  const f = DriveApp.getFoldersByName(CONFIG.DRIVE_FOLDER_NAME);
  if(!f.hasNext()) throw new Error('Không thấy thư mục ' + CONFIG.DRIVE_FOLDER_NAME);
  p.setProperty('DRIVE_FOLDER_ID', f.next().getId());
  Logger.log('OK: đã kết nối thư mục Drive.');
}
function doPost(e){
  try{
    const p = props_(), secret = p.getProperty('BRIDGE_SECRET');
    const payload = JSON.parse((e.postData && e.postData.contents) || '{}');
    if(!secret || payload.secret !== secret) return out_({ok:false,error:'unauthorized'});
    const name = String(payload.fileName||'').trim(), content = String(payload.content||'');
    if(!NAME_OK.test(name)) return out_({ok:false,error:'tên tệp không hợp lệ'});
    if(!content || content.length > CONFIG.MAX_BYTES) return out_({ok:false,error:'nội dung rỗng hoặc quá lớn'});
    const folder = DriveApp.getFolderById(p.getProperty('DRIVE_FOLDER_ID'));
    const hash = md5_(content), key = 'H_' + name;
    if(p.getProperty(key) === hash) return out_({ok:true,status:'UNCHANGED'});
    const ex = folder.getFilesByName(name);
    if(ex.hasNext()){ const f = ex.next(); if(f.getMimeType()===MimeType.GOOGLE_DOCS) DocumentApp.openById(f.getId()).getBody().setText(content); else f.setContent(content); }
    else folder.createFile(name, content, MimeType.PLAIN_TEXT);
    p.setProperty(key, hash);
    return out_({ok:true,status:'SYNCED_TO_DRIVE'});
  }catch(err){ return out_({ok:false,error:String(err.message)}); }
}
function doGet(){ return out_({ok:true,service:'ASTRA bridge'}); }
function syncDriveToGitHub(){
  const p = props_(), token = p.getProperty('GITHUB_TOKEN');
  if(!token) return;
  const files = DriveApp.getFolderById(p.getProperty('DRIVE_FOLDER_ID')).getFiles();
  const cutoff = Date.now() - 24*3600*1000;
  while(files.hasNext()){
    const f = files.next(); if(f.getLastUpdated().getTime() < cutoff) continue;
    let name = f.getName(), mime = f.getMimeType(), content;
    if(mime === MimeType.GOOGLE_DOCS){ content = DocumentApp.openById(f.getId()).getBody().getText(); if(!/\.(md|txt)$/i.test(name)) name += '.md'; }
    else if(mime === MimeType.PLAIN_TEXT || /\.(md|txt)$/i.test(name)) content = f.getBlob().getDataAsString('UTF-8');
    else continue;
    if(!NAME_OK.test(name) || !content.trim() || content.length > CONFIG.MAX_BYTES) continue;
    const hash = md5_(content), key = 'H_' + name;
    if(p.getProperty(key) === hash) continue;
    push_(token, name, content); p.setProperty(key, hash);
  }
}
function push_(token, name, content){
  const url = 'https://api.github.com/repos/'+CONFIG.GITHUB_OWNER+'/'+CONFIG.GITHUB_REPO+'/contents/'+CONFIG.GITHUB_FOLDER+'/'+encodeURIComponent(name);
  const h = {Authorization:'Bearer '+token, Accept:'application/vnd.github+json'};
  const c = UrlFetchApp.fetch(url+'?ref='+CONFIG.GITHUB_BRANCH,{headers:h,muteHttpExceptions:true});
  const body = {message:'Bridge sync từ Drive: '+name, content:Utilities.base64Encode(content,Utilities.Charset.UTF_8), branch:CONFIG.GITHUB_BRANCH};
  if(c.getResponseCode()===200) body.sha = JSON.parse(c.getContentText()).sha;
  const r = UrlFetchApp.fetch(url,{method:'put',headers:h,contentType:'application/json',payload:JSON.stringify(body),muteHttpExceptions:true});
  if(r.getResponseCode()>=300) throw new Error('GitHub '+r.getResponseCode());
}
function md5_(t){ return Utilities.computeDigest(Utilities.DigestAlgorithm.MD5,t,Utilities.Charset.UTF_8).map(function(b){return ('0'+(b&0xFF).toString(16)).slice(-2)}).join(''); }
function out_(o){ return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON); }

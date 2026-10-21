// Zero-build browser client for Supabase Auth + PostgREST.
// No admin keys, publishing tokens, or third-party OAuth credentials belong here.
const $ = id => document.getElementById(id);
let config = null, session = null, selected = null;
const status = msg => { $('status').textContent = msg; };
function show(id){ for(const name of ['setup','auth','editor']) $(name).hidden = name !== id; }
function loadConfig(){ try { return JSON.parse(localStorage.getItem('nassol_cloud_config')); } catch { return null; } }
function validConfig(c){return c && /^https:\/\/[a-z0-9-]+\.supabase\.co$/.test(c.url) && c.key && !c.key.startsWith('sb_secret_');}
async function request(path,{method='GET',body,auth=true}={}){
 const headers={'apikey':config.key,'Content-Type':'application/json'};
 if(auth && session) headers.Authorization='Bearer '+session.access_token;
 const response=await fetch(config.url+path,{method,headers,body:body===undefined?undefined:JSON.stringify(body)});
 const raw=await response.text();let data;try{data=JSON.parse(raw)}catch{data=raw}
 if(!response.ok) throw Error((data && (data.msg||data.message||data.error_description||data.error)) || 'HTTP '+response.status);
 return data;
}
function loginView(){config=loadConfig();show(validConfig(config)?'auth':'setup');}
$('saveConfig').onclick=()=>{const c={url:$('url').value.trim().replace(/\/$/,''),key:$('key').value.trim()};if(!validConfig(c))return status('URL 또는 공개 키를 확인하세요.');localStorage.setItem('nassol_cloud_config',JSON.stringify(c));loginView();status('연결 정보를 저장했습니다.');};
$('reset').onclick=()=>{localStorage.removeItem('nassol_cloud_config');config=null;session=null;show('setup');};
$('login').onclick=async()=>{try{session=await request('/auth/v1/token?grant_type=password',{method:'POST',body:{email:$('email').value.trim(),password:$('password').value},auth:false});$('password').value='';$('identity').textContent=session.user.email;show('editor');await list();status('로그인되었습니다.');}catch(e){status('로그인 실패: '+e.message)}};
$('logout').onclick=()=>{session=null;selected=null;$('password').value='';show('auth');status('로그아웃되었습니다.');};
function clear(){selected=null;$('title').value='';$('body').value='';}
$('new').onclick=clear;
async function persist(state){
 if(!session) return;
 const title=$('title').value.trim(),body=$('body').value;
 if(!title) return status('제목을 입력하세요.');
 const record={title,body,status:state,updated_at:new Date().toISOString()};
 try{
  if(selected){await request('/rest/v1/editorial_drafts?id=eq.'+encodeURIComponent(selected),{method:'PATCH',body:record});}
  else{const created=await request('/rest/v1/editorial_drafts?select=id',{method:'POST',body:{...record,user_id:session.user.id}});selected=created[0].id;}
  await list();status(state==='reviewed'?'검수 완료 상태로 저장했습니다. 발행은 하지 않았습니다.':'클라우드에 저장했습니다.');
 }catch(e){status('저장 실패: '+e.message)}
}
$('save').onclick=()=>persist('draft');
$('review').onclick=()=>persist('reviewed');
async function list(){
 try{
  const rows=await request('/rest/v1/editorial_drafts?select=id,title,body,status,updated_at&order=updated_at.desc&limit=100');
  const holder=$('items');holder.replaceChildren();
  for(const row of rows){
   const a=document.createElement('article'),b=document.createElement('button');
   const heading=document.createElement('strong');heading.textContent=row.title;
   const info=document.createElement('p');info.className='muted';info.textContent=row.status+' · '+new Date(row.updated_at).toLocaleString('ko-KR');
   b.textContent='열어보기';b.onclick=()=>{selected=row.id;$('title').value=row.title;$('body').value=row.body;window.scrollTo(0,0)};
   a.append(heading,info,b);holder.append(a);
  }
 }catch(e){status('목록 불러오기 실패: '+e.message)}
}
loginView();

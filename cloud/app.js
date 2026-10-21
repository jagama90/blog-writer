// Browser-only editorial workbench. No secret keys, login, third-party API calls or automatic publishing.
const $=id=>document.getElementById(id);
const ids=['naver','x','instagram','youtube'];
const storageKey='nassol_editorial_workbench_v1';
const status=msg=>{ $('status').textContent=msg; };
const lines=s=>s.split(/\r?\n/).map(v=>v.trim()).filter(Boolean);
const safe=s=>String(s||'').trim();
const clip=(s,max)=>s.length<=max?s:s.slice(0,max-1).trimEnd()+'…';
const factsText=a=>a.length?a.map(v=>'• '+v).join('\n'):'[방송·기사 등에서 직접 확인한 사실을 입력하세요]';
function input(){return {topic:safe($('topic').value),sources:lines($('sources').value),facts:lines($('facts').value),angle:safe($('angle').value)}}
function generate(){
 const d=input();if(!d.topic)return status('주제를 먼저 입력하세요.');
 if(!d.facts.length)return status('검증된 사실을 최소 한 줄 입력해야 초안을 만들 수 있습니다. 사실을 임의로 생성하지 않습니다.');
 const source=d.sources.length?d.sources.join('\n'):'[출처 URL 추가 필요]';
 const opinion=d.angle||'[개인적인 해석을 추가하세요]';
 $('naverTitle').value=d.topic;
 $('naver').value=`${d.topic}\n\n[도입]\n${d.topic}에서 눈여겨볼 장면과 사실을 정리했습니다.\n\n[확인된 내용]\n${factsText(d.facts)}\n\n[나의 해석]\n${opinion}\n\n[독자에게 질문]\n여러분은 이 장면을 어떻게 보셨나요?\n\n[출처 — 게시 전 직접 확인]\n${source}\n\n#나는SOLO #나솔 #방송리뷰`;
 const xbase=`${d.topic}\n\n${d.facts.slice(0,2).join(' / ')}\n\n${d.angle||'여러분 생각은 어떤가요?'}`;
 $('x').value=clip(xbase,280);
 $('instagram').value=`[1장 표지]\n${d.topic}\n\n[2장 핵심 사실]\n${d.facts[0]}\n\n[3장 추가 맥락]\n${d.facts.slice(1,3).join('\n')||'[추가로 확인한 내용 입력]'}\n\n[4장 해석]\n${opinion}\n\n[5장 참여 유도]\n여러분 생각은?\n\n[게시글 출처]\n${source}`;
 $('youtube').value=`[0~3초 | 후킹]\n${d.topic}\n\n[3~20초 | 확인된 사실]\n${d.facts.slice(0,3).join('\n')}\n\n[20~40초 | 해석]\n${opinion}\n\n[40~50초 | 마무리]\n여러분은 어떻게 생각하세요?\n\n[영상 소스 확인]\n원본 방송 영상·사진의 이용 권한을 확인하세요.\n출처: ${source}`;
 $('results').hidden=false;$('reviewState').textContent='검수 전 · 외부 게시 없음';count();save();status('4개 플랫폼용 편집 초안을 만들었습니다. 실제 AI 집필이나 자동 게시가 아닙니다.');
}
function count(){const n=Array.from($('x').value).length;$('xcount').textContent=`${n}/280자`;$('xcount').style.color=n>280?'#fca5a5':''}
function snapshot(){return {input:input(),outputs:Object.fromEntries(ids.map(id=>[id,$(id).value])),naverTitle:$('naverTitle').value,naverChecks:['checkFacts','checkRights','checkText'].map(id=>$(id).checked),naverState:$('naverState').textContent,review:$('reviewState').textContent,updated_at:new Date().toISOString()}}
function save(){try{localStorage.setItem(storageKey,JSON.stringify(snapshot()));status('현재 기기에 저장했습니다. 다른 기기와 자동 동기화되지 않습니다.')}catch(e){status('저장 실패: '+e.message)}}
function restore(){try{const d=JSON.parse(localStorage.getItem(storageKey)||'null');if(!d)return status('저장된 작업이 없습니다.');$('topic').value=d.input?.topic||'';$('sources').value=(d.input?.sources||[]).join('\n');$('facts').value=(d.input?.facts||[]).join('\n');$('angle').value=d.input?.angle||'';ids.forEach(id=>$(id).value=d.outputs?.[id]||'');$('naverTitle').value=d.naverTitle||d.input?.topic||'';['checkFacts','checkRights','checkText'].forEach((id,i)=>$(id).checked=Boolean(d.naverChecks?.[i]));$('naverState').textContent=d.naverState||'준비 전 · 네이버에 게시되지 않음';$('results').hidden=!ids.some(id=>$(id).value);$('reviewState').textContent=d.review||'검수 전 · 외부 게시 없음';count();status('이전 작업을 불러왔습니다.')}catch(e){status('불러오기 실패: '+e.message)}}
$('generate').onclick=generate;$('restore').onclick=restore;$('saveLocal').onclick=save;
$('approve').onclick=()=>{$('reviewState').textContent='검수 완료 (이 기기에서만 표시) · 외부 게시 없음';save();};
$('export').onclick=()=>{const blob=new Blob([JSON.stringify(snapshot(),null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='nassol-content-'+new Date().toISOString().slice(0,10)+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
document.querySelectorAll('[data-copy]').forEach(b=>b.onclick=async()=>{const id=b.dataset.copy;try{await navigator.clipboard.writeText($(id).value);status(id+' 문구를 복사했습니다.')}catch{ $(id).focus();$(id).select();status('자동 복사 실패: 선택된 내용을 직접 복사해 주세요.')}});
$('x').addEventListener('input',count);

$('copyNaverTitle').onclick=async()=>{try{await navigator.clipboard.writeText($('naverTitle').value);status('네이버 제목을 복사했습니다.')}catch{$('naverTitle').focus();$('naverTitle').select();status('선택된 제목을 직접 복사해 주세요.')}};
$('openNaver').onclick=()=>{window.open('https://blog.naver.com/','_blank','noopener,noreferrer');status('네이버 블로그를 열었습니다. 로그인 후 글쓰기를 선택하세요.')};
$('naverReady').onclick=()=>{const state=$('naverState');if(!['checkFacts','checkRights','checkText'].every(id=>$(id).checked)){state.textContent='검수 항목 3개를 모두 확인해 주세요.';return;}if(!$('naverTitle').value.trim()||!$('naver').value.trim()){state.textContent='네이버 제목과 본문을 입력해 주세요.';return;}state.textContent='발행 준비 완료 · 네이버에 실제 게시된 것은 아닙니다.';try{localStorage.setItem(storageKey,JSON.stringify(snapshot()));}catch(e){status('준비 완료, 단 기기 저장 실패: '+e.message);return;}status('네이버 발행 준비 완료로 표시했습니다. 실제 발행은 하지 않았습니다.');};
['naverTitle','naver','checkFacts','checkRights','checkText'].forEach(id=>$(id).addEventListener('input',()=>{$('naverState').textContent='수정됨 · 발행 준비 재확인 필요';}));

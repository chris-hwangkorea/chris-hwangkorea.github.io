(() => {
  'use strict';
  const $ = id => document.getElementById(id);
  const state = { file:null, originalUrl:'', resultUrl:'', scale:1, zoomIndex:0, panX:0, panY:0, dragging:false };
  const zoomLevels = [1, 2, 4];
  const stageNames = {auto:'색·대비 자동 복원',denoise:'노이즈 제거',sharpen:'디테일 강화',face:'얼굴 강화',old_photo:'오래된 사진 복원',scale2:'AI 2× 확대',scale4:'AI 4× 확대'};
  const endpointKey = 'free-photo-ai-endpoint';

  function status(text,busy=false){$('status').textContent=text;$('progress').value=busy?.5:0}
  function options(){return{auto:$('auto').checked,denoise:$('denoise').checked,sharpen:$('sharpen').checked,face:$('face').checked,old_photo:$('oldPhoto').checked,scale:state.scale}}
  function outputName(name){const p=name.lastIndexOf('.');return p>0?`${name.slice(0,p)}_enhanced.png`:`${name}_enhanced.png`}
  function revoke(key){if(state[key])URL.revokeObjectURL(state[key]);state[key]=''}

  function selectFile(file){
    if(!file||!['image/jpeg','image/png','image/webp'].includes(file.type))return status('JPG, PNG, WebP 파일만 사용할 수 있습니다.');
    if(file.size>20 * 1024 * 1024)return status('파일은 20MB 이하여야 합니다.');
    revoke('originalUrl');revoke('resultUrl');state.file=file;state.originalUrl=URL.createObjectURL(file);
    $('before').src=state.originalUrl;$('after').removeAttribute('src');$('drop').classList.add('hidden');$('compare').classList.remove('hidden');
    $('run').disabled=false;$('save').disabled=true;$('stages').textContent='';status(`${file.name} · 원본은 브라우저에 유지됩니다.`);
  }

  async function run(){
    if(!state.file)return; $('run').disabled=true;$('save').disabled=true;
    const endpoint=$('endpoint').value.trim();
    if(!endpoint){status('Colab 서버 주소를 먼저 붙여 넣어 주세요.');$('run').disabled=false;return}
    status('사진 업로드 및 무료 GPU 처리 중…',true);
    try{
      const {blob,metadata}=await FreePhotoAPI.requestEnhancement(state.file,options(),endpoint);
      revoke('resultUrl');state.resultUrl=URL.createObjectURL(blob);$('after').src=state.resultUrl;$('save').disabled=false;
      $('stages').textContent=metadata.stages.map(x=>stageNames[x]||x).join(' → ');
      status(`웹 AI 완료 · ${metadata.width} × ${metadata.height}`);
    }catch(error){
      if(error.code==='quota_exceeded')status('무료 GPU 한도를 모두 사용했습니다. 다음 무료 사용 가능 시 다시 시도해 주세요.');
      else status(error.message||'네트워크 오류가 발생했습니다. 원본은 그대로 유지됩니다.');
    }finally{$('run').disabled=false}
  }

  function transform(){const z=zoomLevels[state.zoomIndex],v=`translate(${state.panX}px,${state.panY}px) scale(${z})`;[$('before'),$('after')].forEach(x=>x.style.transform=v);$('zoom').textContent=`${z*100}% 확대`}
  function setZoom(index){state.zoomIndex=Math.max(0,Math.min(2,index));if(!state.zoomIndex){state.panX=0;state.panY=0}transform()}
  $('choose').onclick=()=>$('file').click();$('file').onchange=e=>selectFile(e.target.files[0]);$('run').onclick=run;
  $('endpoint').value=localStorage.getItem(endpointKey)||'';
  $('endpoint').oninput=e=>{const value=e.target.value.trim();localStorage.setItem(endpointKey,value);$('connection').textContent=value?'서버 주소 저장됨':'서버 주소가 필요합니다'};
  if($('endpoint').value)$('connection').textContent='서버 주소 저장됨';
  $('save').onclick=()=>{const a=document.createElement('a');a.href=state.resultUrl;a.download=outputName(state.file.name);a.click()};
  document.querySelectorAll('[data-scale]').forEach(b=>b.onclick=()=>{state.scale=Number(b.dataset.scale);document.querySelectorAll('[data-scale]').forEach(x=>x.classList.toggle('active',x===b))});
  $('split').oninput=e=>$('resultClip').style.right=`${100-e.target.value}%`;$('zoom').onclick=()=>setZoom((state.zoomIndex+1)%3);
  const original=show=>$('resultClip').style.visibility=show?'hidden':'visible';$('original').onpointerdown=()=>original(true);['onpointerup','onpointerleave','onpointercancel'].forEach(k=>$('original')[k]=()=>original(false));
  $('compare').onpointerdown=e=>{if(!state.zoomIndex||['split','zoom','original'].includes(e.target.id))return;state.dragging=true;state.lastX=e.clientX;state.lastY=e.clientY};
  $('compare').onpointermove=e=>{if(!state.dragging)return;state.panX+=e.clientX-state.lastX;state.panY+=e.clientY-state.lastY;state.lastX=e.clientX;state.lastY=e.clientY;transform()};
  $('compare').onpointerup=() => state.dragging=false;$('compare').onwheel=e=>{e.preventDefault();setZoom(state.zoomIndex+(e.deltaY<0?1:-1))};
  ['dragover','drop'].forEach(type=>$('drop').addEventListener(type,e=>e.preventDefault()));$('drop').ondrop=e=>selectFile(e.dataTransfer.files[0]);
})();

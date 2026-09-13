'use strict';
const $ = id => document.getElementById(id);
const names = {persistence:'Persistence',linear_trend:'Linear trend',arima:'ARIMA',lstm:'LSTM',trend_only:'Trend only',arima_growth:'ARIMA + trend',lstm_growth:'LSTM + trend',always_off:'Always off'};
const colors = {actual:'#192e39',lstm:'#e05b5b',arima:'#8164ba',persistence:'#009a8e',linear_trend:'#c98922'};
let meta, currentReplay, currentLive, dataset='antarex_mono', index=360, page='replay', playing=false, replayBusy=false, liveBusy=false, inferenceBusy=false, generation=0, lastTick=0, lastLivePoll=0, remainder=0;
const number = (x,d=2) => x === null || x === undefined ? '—' : Number(x).toFixed(d);
const pct = x => x === null || x === undefined ? '—' : number(x*100)+'%';
const info = () => meta.datasets.find(d => d.id===dataset);
const minutes = (t,start) => number((t-start)/60,1)+' min';
function error(message){$('error').textContent=message; $('error').hidden=!message;}
async function api(path,body){const options=body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json','X-Demo-Token':meta.token},body:JSON.stringify(body)};const response=await fetch(path,options);const data=await response.json();if(!response.ok)throw Error(data.error||'Request failed');return data;}
function element(tag,attrs={},text){const e=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([k,v])=>e.setAttribute(k,String(v)));if(text!==undefined)e.textContent=text;return e;}
function plot(id,observations,forecasts,cadence,cursor,showLabels=false){
  const svg=$(id);svg.replaceChildren();
  if(!observations.length){svg.append(element('text',{x:540,y:155,'text-anchor':'middle'},'Start a session to see measured memory here.'));return;}
  const left=58,right=1060,top=24,bottom=280,start=observations[0].t;
  const end=Math.max(start+cadence*2,cursor,...forecasts.map(p=>p.target));
  const values=observations.map(p=>p.memory*100).concat(forecasts.flatMap(p=>Object.keys(colors).filter(k=>k!=='actual').map(k=>p[k]===null||p[k]===undefined?null:p[k]*100)).filter(x=>x!==null));
  let lo=Math.max(0,Math.min(...values)-.25),hi=Math.min(100,Math.max(...values)+.25);if(hi-lo<.5)hi=lo+.5;
  const x=t=>left+(t-start)/(end-start)*(right-left),y=v=>bottom-(v*100-lo)/(hi-lo)*(bottom-top);
  if(showLabels)for(const p of observations)if(p.leak===1){const finish=Math.min(cursor,p.t+cadence);if(finish>p.t)svg.append(element('rect',{x:x(p.t),y:top,width:Math.max(0,x(finish)-x(p.t)),height:bottom-top,fill:'#fbeaea'}));}
  for(let i=0;i<=4;i++){const value=lo+(hi-lo)*i/4,yy=bottom-(bottom-top)*i/4;svg.append(element('line',{x1:left,x2:right,y1:yy,y2:yy,stroke:'#e3ebed'}),element('text',{x:left-10,y:yy+4,'text-anchor':'end'},number(value,1)+'%'));}
  for(let i=0;i<=5;i++){const t=start+(end-start)*i/5;svg.append(element('text',{x:x(t),y:bottom+23,'text-anchor':'middle'},number((t-start)/60,1)));}
  svg.append(element('text',{x:(left+right)/2,y:324,'text-anchor':'middle'},'Minutes from the start of this visible window'));
  function line(points,color,dashed){let previous=null,d='';for(const p of points){if(!Number.isFinite(p.v)){previous=null;continue;}const move=previous===null||p.t-previous>cadence*2.5;d+=(move?'M':'L')+x(p.t).toFixed(2)+','+y(p.v).toFixed(2)+' ';previous=p.t;}if(d)svg.append(element('path',{d,fill:'none',stroke:color,'stroke-width':dashed?1.8:2.7,'stroke-dasharray':dashed?'6 4':'none','stroke-linejoin':'round'}));}
  for(const model of ['linear_trend','persistence','arima','lstm'])line(forecasts.map(p=>({t:p.target,v:p[model]})),colors[model],true);
  line(observations.map(p=>({t:p.t,v:p.memory})),colors.actual,false);
  const last=observations[observations.length-1];svg.append(element('circle',{cx:x(last.t),cy:y(last.memory),r:4,fill:colors.actual}));
  svg.append(element('line',{x1:x(cursor),x2:x(cursor),y1:top,y2:bottom,stroke:'#78989f','stroke-dasharray':'3 4'}),element('text',{x:Math.min(right-30,x(cursor)+6),y:15},'Now'));
}
function setPlaying(value){playing=value;lastTick=performance.now();remainder=0;$('play').textContent=value?'Pause replay':'Play replay';}
function renderReplay(data){
  currentReplay=data;const r=data.current,rule=$('rule').value,d=info(),active=r[rule+'_warning'];
  $('memory').textContent=pct(r.memory_pressure_at_origin);$('forecast').textContent=pct(r.lstm_forecast);$('growth').textContent=number(r.observed_growth_pp_per_minute,3);$('horizon').textContent=d.horizon+' seconds ahead · saved LSTM';$('time-label').textContent=minutes(r.origin_timestamp,d.start)+' into the test recording';
  $('warning').textContent=active?'Warning active':'No active warning';$('warning-card').classList.toggle('warning',active);
  $('warning-context').textContent=(r.label_known?'Recorded injection: '+(r.leak_active===1?'active':'inactive'):'Leak labels unavailable')+' · '+names[rule];
  $('cursor').value=data.index;$('position').textContent=(data.index+1).toLocaleString()+' / '+data.count.toLocaleString();
  plot('replay-chart',data.observations,data.forecasts,d.cadence,r.origin_timestamp,$('labels').checked&&d.id==='antarex_mono');
  $('alarms').replaceChildren();
  const alarms=data.alarms.filter(a=>a.rule===rule);
  for(const alarm of alarms){const row=document.createElement('div');row.className='alarm-row';const t=document.createElement('span'),s=document.createElement('span');t.textContent=minutes(alarm.t,d.start);s.textContent=alarm.recorded_leak===null?'Label unknown':alarm.recorded_leak===1?'During recorded injection':'Outside recorded leak';row.append(t,s);$('alarms').append(row);}
  if(!alarms.length)$('alarms').textContent='No alarm starts for this rule before the cursor.';
}
async function loadReplay(){
  if(replayBusy)return;replayBusy=true;$('infer').disabled=true;const requested=generation;
  try{const data=await api('/api/replay?'+new URLSearchParams({dataset,index,window:360}));if(requested===generation){renderReplay(data);error('');}}
  catch(e){setPlaying(false);error(e.message);}finally{replayBusy=false;$('infer').disabled=inferenceBusy||!meta.inference_available;if(requested!==generation)loadReplay();}
}
function chooseDataset(value){dataset=value;generation++;setPlaying(false);index=Math.min(360,info().count-1);$('cursor').max=info().count-1;$('jump').disabled=info().first_leak_index===null;$('labels').disabled=dataset!=='antarex_mono';$('inference').textContent='Run the selected saved weights on the same 60 past observations and compare with the archived forecast.';$('features').replaceChildren();for(const name of info().features){const chip=document.createElement('span');chip.textContent=name.replaceAll('_',' ');$('features').append(chip);}$('replay-scope').textContent=dataset==='antarex_mono'?'Controlled leak injections on a real machine. Peak observed memory pressure in the source block was 42.24%; warning lead time before exhaustion was not evaluated.':'Real-workload recording with unknown leak labels. Alarm counts are descriptive; leak precision, recall and false-alarm rates cannot be established.';loadReplay();}
function buildResults(){
  for(const d of meta.datasets)for(const model of ['persistence','linear_trend','arima','lstm']){const r=meta.forecast_metrics.find(r=>r.dataset===d.id&&r.model===model);const tr=document.createElement('tr');if(model==='lstm')tr.className='highlight';for(const value of [d.title,names[model],Number(r.n).toLocaleString(),number(r.mae_percentage_points,6),number(r.rmse_percentage_points,6)]){const td=document.createElement('td');td.textContent=value;tr.append(td);}$('forecast-results').append(tr);}
  for(const rule of ['trend_only','lstm_growth','arima_growth','always_off']){const r=meta.warning_metrics.find(r=>r.method===rule),e=meta.event_metrics.find(r=>r.method===rule),tr=document.createElement('tr');for(const value of [names[rule],r.precision===null?'Undefined':number(r.precision,4),number(r.recall,4),number(r.f1,4),number(r.false_alarm_starts_per_non_leak_hour,3),e.detected_events+' / '+e.eligible_events,e.median_delay_seconds_detected_only===null?'Undefined':number(e.median_delay_seconds_detected_only,0)+' s']){const td=document.createElement('td');td.textContent=value;tr.append(td);}$('warning-results').append(tr);}
}
function renderLive(data){
  currentLive=data;const r=data.rows.at(-1);$('start-live').disabled=data.running;$('stop-live').disabled=!data.running;$('live-threshold').disabled=data.running;$('export-live').disabled=!r;$('live-count').textContent=data.rows.length;
  $('live-state').textContent=data.running?'Recording every '+data.cadence+' seconds…':data.session?'Session stopped. Data saved locally.':'Collection is off.';
  if(data.error)error(data.error);
  if(!r){plot('live-chart',[],[],5,0);return;}
  $('live-memory').textContent=pct(r.memory_pressure);$('live-capacity').textContent=number(r.available_memory_bytes/2**30)+' / '+number(r.total_memory_bytes/2**30)+' GiB available';$('live-cpu').textContent=r.cpu_percent===null?'Warming up':number(r.cpu_percent,1)+'%';$('live-forecast').textContent=pct(r.linear_trend_60s);
  $('live-warning').textContent=!r.ready?'Warming up':r.warning?'Growth warning':'No active warning';$('live-warning-card').classList.toggle('warning',r.warning);$('live-ready').textContent=r.ready?'Growth: '+number(r.growth_pp_per_minute,3)+' pp/min':r.samples_until_ready+' more samples for a trend estimate';
  $('live-swap').textContent=number(r.swap_used_bytes/2**30)+' GiB';$('live-disk').textContent=number(r.disk_read_bytes_per_second===null?null:r.disk_read_bytes_per_second/2**20)+' / '+number(r.disk_write_bytes_per_second===null?null:r.disk_write_bytes_per_second/2**20);$('live-faults').textContent=r.page_faults_per_second===null?'Unavailable':number(r.page_faults_per_second,1);
  const rows=data.rows.slice(-360);plot('live-chart',rows.map(p=>({t:p.timestamp,memory:p.memory_pressure})),rows.filter(p=>p.linear_trend_60s!==null).map(p=>({target:p.timestamp+60,linear_trend:p.linear_trend_60s})),data.cadence,r.timestamp);
}
async function pollLive(){if(liveBusy)return;liveBusy=true;try{renderLive(await api('/api/live'));}catch(e){error(e.message);}finally{liveBusy=false;}}
async function changePage(value){page=value;setPlaying(false);document.querySelectorAll('.page').forEach(e=>e.hidden=e.id!==value+'-page');document.querySelectorAll('.nav').forEach(e=>e.classList.toggle('active',e.dataset.page===value));$('page-title').textContent={replay:'Experiment replay',live:'Live monitor',results:'Results & evidence'}[value];$('page-description').textContent={replay:'Explore measured memory, saved forecasts and warnings one observation at a time.',live:'Observe this computer’s memory and sustained growth as it happens.',results:'Trace the preliminary findings back to the verified experiment outputs.'}[value];$('source-badge').textContent=value==='live'?'This computer · exploratory':'Verified Colab recordings';error('');if(value==='live')await pollLive();}
async function initialize(){try{
  meta=await api('/api/metadata');for(const d of meta.datasets)for(const id of ['dataset','learning-dataset']){const o=document.createElement('option');o.value=d.id;o.textContent=d.title;$(id).append(o);}
  $('source-badge').textContent='Verified Colab recordings';$('integrity').textContent=meta.verified_files+' source files passed integrity checks';$('infer').disabled=!meta.inference_available;if(!meta.inference_available)$('infer').title='Restore the preprocessing ZIP using the README instructions.';
  $('learning-figure').src='/figures/antarex_mono-learning.png';buildResults();chooseDataset(dataset);
  document.querySelectorAll('.nav').forEach(b=>b.addEventListener('click',()=>changePage(b.dataset.page)));
  $('dataset').addEventListener('change',e=>chooseDataset(e.target.value));$('rule').addEventListener('change',()=>currentReplay&&renderReplay(currentReplay));$('labels').addEventListener('change',()=>currentReplay&&renderReplay(currentReplay));
  $('play').addEventListener('click',()=>{if(index>=info().count-1)index=0;setPlaying(!playing);});$('restart').addEventListener('click',()=>{setPlaying(false);index=0;generation++;loadReplay();});
  $('cursor').addEventListener('input',e=>{setPlaying(false);index=Number(e.target.value);generation++;loadReplay();});$('jump').addEventListener('click',()=>{setPlaying(false);index=Math.max(0,info().first_leak_index-12);generation++;loadReplay();});
  $('export-replay').addEventListener('click',()=>{if(currentReplay)window.location.href='/api/export/replay?'+new URLSearchParams({dataset:currentReplay.dataset,index:currentReplay.index,window:360});});
  $('infer').addEventListener('click',async()=>{
    if(replayBusy||inferenceBusy||!currentReplay||currentReplay.dataset!==dataset)return;
    setPlaying(false);inferenceBusy=true;$('infer').disabled=true;const requested=generation,selectedIndex=currentReplay.index;
    $('inference').textContent='Loading weights and running this history…';
    try{const r=await api('/api/infer',{dataset,index:selectedIndex});if(requested===generation&&index===selectedIndex)$('inference').textContent=(r.matches_saved?'Matches the saved forecast. ':'Difference detected. ')+'Computed '+pct(r.prediction)+'; saved '+pct(r.saved_prediction)+'. Difference: '+r.absolute_difference_fraction.toExponential(2)+' of total RAM. Request computation: '+number(r.elapsed_ms,1)+' ms (includes first model load).';}
    catch(e){if(requested===generation)$('inference').textContent=e.message;}
    finally{inferenceBusy=false;$('infer').disabled=replayBusy||!meta.inference_available;}
  });
  $('learning-dataset').addEventListener('change',e=>{$('learning-figure').src='/figures/'+e.target.value+'-learning.png';});
  $('start-live').addEventListener('click',async()=>{try{error('');renderLive(await api('/api/live/start',{threshold:Number($('live-threshold').value)}));}catch(e){error(e.message);}});
  $('stop-live').addEventListener('click',async()=>{try{renderLive(await api('/api/live/stop',{}));}catch(e){error(e.message);}});$('export-live').addEventListener('click',()=>{window.location.href='/api/export/live';});
  setInterval(()=>{const now=performance.now();if(page==='live'&&now-lastLivePoll>=1000){lastLivePoll=now;pollLive();}if(!playing||page!=='replay'||replayBusy)return;remainder+=(now-lastTick)*Number($('speed').value)/(info().cadence*1000);lastTick=now;const steps=Math.floor(remainder);if(steps){remainder-=steps;index=Math.min(info().count-1,index+steps);if(index>=info().count-1)setPlaying(false);loadReplay();}},250);
}catch(e){error('Dashboard could not load: '+e.message);}}
initialize();

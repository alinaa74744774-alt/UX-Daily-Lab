(() => {
"use strict";
const MODULES=["learn","english","challenge","practice","review"];
const LABELS={learn:"Learn",english:"English",challenge:"Challenge",practice:"Practice",review:"Review"};
const el=id=>document.getElementById(id);
const safe=s=>String(s==null?"":s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
function englishOnly(source){
 return String(source||"").replace(/\r/g,"").split("\n")
  .filter(line=>!/(?:中文理解|中文解释|中文辅助|中文翻译|中文支持|字段填写说明|短语释义)/.test(line))
  .map(line=>line.replace(/[\u3400-\u9fff\uF900-\uFAFF]/g,"").replace(/｜/g," — ").replace(/[：；、，。！？（）【】《》]/g," ").replace(/\(\s*\)|\[\s*\]/g,"").replace(/\s{2,}/g," ").trim())
  .filter(line=>line&&(/[A-Za-z0-9]/.test(line)||/^[-*_|\x60]{3,}$/.test(line)))
  .join("\n");
}
let courses=[],current=null,state=blank(),toastTimer;
function blank(){return {learn:false,english:false,challenge:false,practice:false,review:false,reflection:""}}
function mdInline(s){return safe(s).replace(/\*\*([^*]+)\*\*/g,"<strong>$1</strong>").replace(/\*([^*]+)\*/g,"<em>$1</em>")}
function renderMd(source){
 const lines=String(source||"").replace(/\r/g,"").split("\n");let out="",list="",quote=false,table=false,code=null;
 const cl=()=>{if(list){out+="</"+list+">";list=""}},cq=()=>{if(quote){out+="</blockquote>";quote=false}},ct=()=>{if(table){out+="</tbody></table>";table=false}};
 for(const raw of lines){const x=raw.trim();if(code!==null){if(/^\x60\x60\x60/.test(x)){out+='<pre class="markdown-code"><code>'+safe(code.join("\n"))+'</code></pre>';code=null}else code.push(raw);continue}if(/^\x60\x60\x60/.test(x)){cl();cq();ct();code=[];continue}if(!x){cl();cq();ct();continue}
  if(/^\|.*\|$/.test(x)){cl();cq();const cells=x.slice(1,-1).split("|").map(y=>y.trim());if(cells.every(y=>/^:?-{3,}:?$/.test(y)))continue;if(!table){out+="<table><thead><tr>"+cells.map(y=>"<th>"+mdInline(y)+"</th>").join("")+"</tr></thead><tbody>";table=true}else out+="<tr>"+cells.map(y=>"<td>"+mdInline(y)+"</td>").join("")+"</tr>";continue}
  ct();const h=x.match(/^(#{1,4})\s+(.*)$/);if(h){cl();cq();const n=h[1].length;out+="<h"+n+">"+mdInline(h[2])+"</h"+n+">";continue}
  if(/^---+$/.test(x)){cl();cq();out+="<hr>";continue}
  if(/^>\s?/.test(x)){cl();if(!quote){out+="<blockquote>";quote=true}out+="<p>"+mdInline(x.replace(/^>\s?/,""))+"</p>";continue}
  cq();const u=x.match(/^[-*]\s+(.*)$/),o=x.match(/^\d+\.\s+(.*)$/);if(u||o){const k=u?"ul":"ol";if(list!==k){cl();out+="<"+k+">";list=k}out+="<li>"+mdInline((u||o)[1])+"</li>";continue}
  cl();out+="<p>"+mdInline(x)+"</p>";
 }
 if(code!==null)out+='<pre class="markdown-code"><code>'+safe(code.join("\n"))+'</code></pre>';
 cl();cq();ct();return out;
}
function sections(md){
 let out=[],cur=null,inFence=false;
 for(const line of String(md||"").replace(/\r/g,"").split("\n")){
  if(/^\s*\x60\x60\x60/.test(line)){if(cur)cur.body.push(line);inFence=!inFence;continue}
  const m=!inFence&&line.match(/^##\s+(.*)$/);
  if(m){cur={heading:m[1].trim(),body:[]};out.push(cur)}
  else if(cur)cur.body.push(line)
 }
 out.forEach(x=>x.body=x.body.join("\n").trim());return out
}
function norm(s){return String(s||"").replace(/^\d+\s*/,"").replace(/[｜|]/g," ").replace(/\s+/g," ").trim().toLowerCase()}
function findSec(list,re){return list.find(x=>re.test(norm(x.heading)))||null}
function getLegacy(s){return {goal:findSec(s,/^research goal/),method:findSec(s,/^research method/),target:findSec(s,/^target user/),questions:findSec(s,/^(interview questions|neutral follow-up)/),notes:findSec(s,/^note-taking and synthesis/),criteria:findSec(s,/^completion checklist/),session:findSec(s,/^suggested (45-minute )?session/) }}
function getContent(md,s){
 const learn=findSec(s,/^learn(?:\s|$)/),english=findSec(s,/^(ux )?english(?:\s|$)/),challenge=findSec(s,/^(daily ux )?challenge(?:\s|$)/),practice=findSec(s,/^(practice|mini project|deliverable)(?:\s|$)/),review=findSec(s,/^(review|reflection prompt)(?:\s|$)/),old=getLegacy(s);
 return {learn:learn?learn.body:[old.goal,old.method,old.target,old.questions].filter(Boolean).map(x=>"## "+x.heading+"\n\n"+x.body).join("\n\n"),english:english?english.body:"",challenge:challenge?challenge.body:[old.criteria,old.session].filter(Boolean).map(x=>"## "+x.heading+"\n\n"+x.body).join("\n\n"),practice:practice?practice.body:[old.questions,old.notes,old.session].filter(Boolean).map(x=>"## "+x.heading+"\n\n"+x.body).join("\n\n"),review:review?review.body:"",legacy:!challenge};
}
function blocks(source){let a=[],cur=null;for(const line of String(source||"").replace(/\r/g,"").split("\n")){const m=line.match(/^#{2,3}\s+(.*)$/);if(m){cur={title:m[1].trim(),body:[]};a.push(cur)}else if(cur)cur.body.push(line);else if(line.trim()){cur={title:"",body:[]};a.push(cur);cur.body.push(line)}}return a.map(x=>({...x,body:x.body.join("\n").trim()})).filter(x=>x.title||x.body)}
function renderLearn(c,ss){
 const sec=findSec(ss,/^learn(?:\s|$)|^today.?s idea|^ux fundamentals/),old=getLegacy(ss);let items=[];
 if(sec){items=blocks(sec.body);if(!items.length)items=[{title:sec.heading,body:sec.body}];if(items.length===1&&!items[0].title)items[0].title=sec.heading}
 else{if(old.goal)items.push({title:"User Research",kind:"FOUNDATION",body:old.goal.body,subtitle:"Research replaces assumptions."});if(old.method)items.push({title:"Semi-structured Interview",kind:"METHOD",body:old.method.body});const principle=findSec(ss,/^note-taking and synthesis/);if(principle)items.push({title:"Evidence over Assumptions",kind:"PRINCIPLE",body:principle.body});else if(old.target)items.push({title:"Target User",kind:"PRINCIPLE",body:old.target.body})}
 if(!items.length)return '<article class="concept-card concept-feature"><span class="card-kicker">CORE IDEA</span><h3>'+safe(englishTopic(c))+'</h3><p>Explore today’s UX idea through the course source.</p><div class="card-foot">WHY IT MATTERS</div></article>';
 const kinds=["FOUNDATION","METHOD","PRINCIPLE"],tags=["WHY IT MATTERS","HOW TO EXPLORE","HOW TO INTERPRET"];let html="";
 items.slice(0,3).forEach((x,i)=>{if(i)html+='<div class="sequence-connector" aria-hidden="true"><span>'+(i===1?"WHY":"HOW")+'</span><i><svg width="16" height="16" class="ui-icon arrow-down-icon" viewBox="0 0 18 18" aria-hidden="true" focusable="false" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"><path d="M9 3v12M4.5 10.5 9 15l4.5-4.5"/></svg></i></div>';const first=i===0,title=x.title||kinds[i],kind=x.kind||kinds[i],body=x.body||"",eng=body.split(/\r?\n/).filter(z=>!/(?:中文理解|中文解释|中文辅助理解)：/.test(z)).join("\n").trim(),zh=[...body.matchAll(/(?:中文理解|中文解释|中文辅助理解)[：:]\*{0,2}\s*([^\n]+)/g)].map(m=>m[1].replace(/\*\*/g,"").trim()).filter(Boolean).join(" ");html+='<article class="concept-card '+(first?"concept-feature":"sequence-card")+'"><span class="'+(first?"card-kicker":"concept-number")+'">'+(first?kind+' <span>01</span>':String(i+1).padStart(2,"0")+' · '+kind)+'</span><h3>'+safe(title)+'</h3>'+(x.subtitle?'<p class="concept-subtitle">'+safe(x.subtitle)+'</p>':'')+'<div class="markdown-content">'+renderMd(eng)+'</div>'+(zh?'<p class="zh">'+safe(zh.replace(/\*\*/g,""))+'</p>':'')+(first?'<div class="card-foot">WHY IT MATTERS</div>':'<div class="tag">'+tags[i]+'</div>')+'</article>'});
 return html;
}
function txtFirst(s){for(const raw of String(s||"").split(/\r?\n/)){const x=raw.trim();if(!x||/^#{1,4}\s|^[|>*-]/.test(x)||/^中文(?:理解|解释)/.test(x))continue;const y=x.replace(/\*\*/g,"").replace(/\*/g,"").trim();if(y)return y}return ""}
function zhSupport(s){const m=String(s||"").match(/(?:中文理解|中文解释|中文辅助理解)[：:]\*{0,2}\s*(.+)/);return m?m[1].replace(/\*\*/g,"").trim():""}
function splitTerm(s){const m=String(s||"").match(/^(.+?)\s+([\u3400-\u9fff].*)$/);return m?{en:m[1].trim(),zh:m[2].trim()}:{en:s,zh:""}}
function value(body,re){const m=String(body||"").match(re);return m?m[1].trim().replace(/^["“]|["”]$/g,""):""}
function vocab(md){
 const sec=findSec(sections(englishOnly(md)),/^(ux )?english(?:\s|$)/);if(!sec)return {cards:[],phrases:[]};
 const terms=[...sec.body.matchAll(/^###\s+\d+[.)]?\s+(.+)$/gm)];
 const cards=terms.map((m,i)=>{const start=m.index+m[0].length,end=terms[i+1]?terms[i+1].index:sec.body.length,b=sec.body.slice(start,end),t=splitTerm(m[1]),d=value(b,/^\s*-?\s*\*\*(?:English definition|Definition):\*\*\s*(.+)$/mi)||value(b,/^\s*(?:English definition|Definition):\s*(.+)$/mi),ex=value(b,/^\s*-?\s*\*\*(?:UX-context example|UX example):\*\*\s*(.+)$/mi)||value(b,/^\s*(?:UX-context example|UX example):\s*(.+)$/mi);return '<article class="vocab-card"><div class="vocab-title"><span class="vocab-index">0'+(i+1)+'</span><h3>'+safe(t.en)+'</h3></div><p class="vocab-def">'+safe(d)+'</p><div class="vocab-example"><b>UX CONTEXT EXAMPLE</b><p>“'+safe(ex.replace(/^["“]|["”]$/g,""))+'”</p></div></article>'});
 let phrases=[];const pm=sec.body.match(/^#{3,4}\s+(?:Professional UX Expressions|Professional Expressions|Phrases to remember)[^\n]*\n([\s\S]*)/mi);if(pm){const body=pm[1].split(/^#{3,4}\s+/m)[0];for(const m of body.matchAll(/^\s*[-*]\s*\*\*["“]?([^"”]+)["”]?\*\*\s*[—–-]\s*(.+)$/gm)){phrases.push('<div class="phrase-item"><span class="phrase-icon">“</span><div><b>'+safe(m[1].trim())+'</b><p>'+safe(m[2].trim())+'</p></div></div>')}}
 return {cards,phrases};
}
function dayWeek(d){return Math.floor((d-1)/7)+1}
function normCourse(x){const d=Number(x.day),p=typeof x.content_path==="string"?x.content_path.trim():"",s=String(x.generation_status||x.status||"").toLowerCase();return {...x,day:d,week:dayWeek(d),path:p,available:!!p&&(["existing","available","active","completed"].includes(s)||x.generation_status==="generated"),title:String(x.title||("Day "+String(d).padStart(2,"0"))),topic:String(x.topic||x.title||""),scheduled_date:String(x.scheduled_date||"")}}
function flatten(m){if(!m||!Array.isArray(m.weeks))throw Error("Unsupported manifest schema");const a=m.weeks.flatMap(w=>Array.isArray(w.days)?w.days:[]).map(normCourse).filter(x=>Number.isInteger(x.day)&&x.day>0).sort((x,y)=>x.day-y.day),seen=new Set();for(const x of a){if(seen.has(x.day))throw Error("Duplicate Day "+x.day+" in manifest");seen.add(x.day);if(x.path&&(x.path.startsWith("/")||x.path.split("/").includes("..")))throw Error("Unsafe Markdown path in manifest")}return a}
function cnDate(){const p=new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Shanghai",year:"numeric",month:"2-digit",day:"2-digit"}).formatToParts(new Date()),o=Object.fromEntries(p.map(x=>[x.type,x.value]));return o.year+"-"+o.month+"-"+o.day}
function dayLabel(c){return "DAY "+String(c.day).padStart(2,"0")}
function englishTopic(c){const t=(c.topic||c.title).replace(/^Day\s*\d+\s*[｜|:：-]\s*/i,"").trim(),m=t.match(/[A-Za-z][A-Za-z0-9 /&×-]*/);return (m?m[0]:t).trim()}
function chineseTopic(c){const t=(c.title+" "+c.topic).replace(/^Day\s*\d+\s*[｜|:：-]\s*/i,""),m=t.match(/[\u3400-\u9fff][\u3400-\u9fff\s·、（）()]*/);return m?m[0].trim():""}
function key(d){return "uxdl-day-"+String(d).padStart(2,"0")+"-modules-v3"}
function readState(c){const s=blank();if(!c)return s;try{let x=JSON.parse(localStorage.getItem(key(c.day))||"null");if(!x&&c.day===1){x=JSON.parse(localStorage.getItem("uxdl-day01-modules-v2")||"null")||JSON.parse(localStorage.getItem("uxdl-day01-status")||"null")||JSON.parse(localStorage.getItem("uxd1-day01-status")||"null");if(x){s.learn=x.learn===true||x.learning===true;s.english=x.english===true;s.challenge=x.challenge===true;s.practice=x.practice===true;s.review=x.review===true;s.reflection=typeof x.reflection==="string"?x.reflection:"";localStorage.setItem(key(c.day),JSON.stringify(s));return s}}if(x&&typeof x==="object")return {learn:x.learn===true||x.learning===true,english:x.english===true,challenge:x.challenge===true,practice:x.practice===true,review:x.review===true,reflection:typeof x.reflection==="string"?x.reflection:""}}catch(_){}return s}
function isDone(c){return MODULES.every(k=>readState(c)[k]===true)}
function buildNav(){
 const nav=el("weekNav"),groups=new Map();courses.forEach(c=>{if(!groups.has(c.week))groups.set(c.week,[]);groups.get(c.week).push(c)});
 nav.innerHTML=[...groups.entries()].map(([week,items])=>{const done=items.filter(c=>c.available&&isDone(c)).length,active=items.filter(c=>current&&c.available&&current.day===c.day&&!isDone(c)).length,up=items.filter(c=>!c.available).length;
  const rows=items.map(c=>{const selected=current&&current.day===c.day&&c.available,complete=c.available&&isDone(c),label=englishTopic(c),inner='<span class="day-num">'+String(c.day).padStart(2,"0")+'</span><span class="day-title">'+safe(label)+'</span><span class="day-status" title="'+(complete?"Completed":selected?"Active":c.available?"Available":"Upcoming")+'">'+(complete?'<span class="day-check-mark">✓</span>':selected?'<span class="day-status-dot"></span>':c.available?'<span class="day-available-mark">•</span>':'<span class="day-upcoming-mark">·</span>')+'</span>';
   return c.available?'<a class="day-link'+(selected?" active":"")+(complete?" completed":"")+'" href="#top" data-course-day="'+c.day+'"'+(selected?' aria-current="page"':"")+'>'+inner+'</a>':'<button class="day-link upcoming" type="button" data-upcoming-day="'+c.day+'">'+inner+'</button>'
  }).join("");
  return rows+'<div class="week-note">WEEK '+String(week).padStart(2,"0")+' <span>'+done+' completed · '+active+' active · '+up+' upcoming</span></div>'
 }).join("");
 nav.querySelectorAll("[data-course-day]").forEach(a=>a.addEventListener("click",e=>{e.preventDefault();const c=courses.find(x=>x.day===Number(a.dataset.courseDay));if(c)selectCourse(c);closeNav();window.scrollTo({top:0,behavior:"smooth"})}));
 nav.querySelectorAll("[data-upcoming-day]").forEach(b=>b.addEventListener("click",()=>showUpcoming(Number(b.dataset.upcomingDay))))
}
function closeNav(){const rail=document.querySelector(".rail"),toggle=el("menuToggle");if(rail)rail.classList.remove("open");if(toggle)toggle.setAttribute("aria-expanded","false")}
function showUpcoming(d){const c=courses.find(x=>x.day===d);if(!c)return;el("dialogDay").textContent=dayLabel(c);el("upcomingTitle").textContent=englishTopic(c)||c.title;el("dialogStatus").textContent="UPCOMING · NOT AVAILABLE YET";el("dialogCopy").textContent=c.scheduled_date?"This lesson is planned for "+c.scheduled_date+". Its course is not available yet.":"This lesson appears in the Project plan, but its course is not available yet.";const dlg=el("upcomingDialog");if(dlg&&dlg.showModal)dlg.showModal()}
function mdUrl(path){return "./"+path.split("/").map(encodeURIComponent).join("/")}
function set(id,v){const n=el(id);if(n&&v)n.textContent=v}
function renderChallenge(course,c){
 const parts=blocks(englishOnly(c.challenge)),pick=re=>parts.find(x=>re.test(x.title)),old=getLegacy(c.sections);
 const scenario=pick(/^scenario$/i),goal=pick(/^(learning )?goal$/i),deliverable=pick(/^deliverable$/i),criteria=pick(/completion criteria|completion checklist|success criteria|definition of done/i);
 const scenarioText=scenario?scenario.body:(old.target&&old.target.body)||"Apply today's UX idea to a real product situation.";
 const goalText=goal?goal.body:(old.goal&&old.goal.body)||"Use today's UX idea to make a clear design decision.";
 const deliverableText=deliverable?deliverable.body:(course.day===1?"A concise interview plan with three open-ended questions and neutral follow-up probes.":old.questions&&old.questions.body||"A focused UX artifact that applies today's lesson.");
 const criteriaText=criteria?criteria.body:(old.criteria&&old.criteria.body)||"Complete the deliverable and explain the reasoning behind your decisions.";
 const duration=(String(c.practice||"").match(/\b\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||String(c.challenge||"").match(/\b\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||old.session&&old.session.heading.match(/\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||[])[0]||"";
 return '<div class="challenge-main"><div class="challenge-label"><span class="challenge-icon"><svg width="16" height="16" class="ui-icon sparkle-icon" viewBox="0 0 18 18" aria-hidden="true" focusable="false" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.6"><path d="m9 2 1.7 5.3L16 9l-5.3 1.7L9 16l-1.7-5.3L2 9l7-2.7L9 2Z"/></svg></span> SCENARIO · TODAY’S CHALLENGE</div><h3>'+safe(txtFirst(scenarioText)||englishTopic(course))+'</h3><div class="challenge-fields"><div><b>GOAL</b>'+renderMd(goalText)+'</div><div><b>DELIVERABLE</b>'+renderMd(deliverableText)+'</div></div><button class="module-complete-button" type="button" data-complete-module="challenge" aria-pressed="false"><span class="module-check"></span><span class="module-label">Mark Challenge Complete</span></button></div><aside class="criteria-card"><div class="criteria-head"><span>✓</span><div><b>Completion Criteria</b></div></div><div class="markdown-content criteria-render">'+renderMd(criteriaText)+'</div><div class="criteria-time"><b>ESTIMATED TIME</b><span>'+(duration?safe(duration)+' · from the course':'See the Practice section')+'</span></div></aside>';
}
function render(course,sourceMarkdown){
 const md=englishOnly(sourceMarkdown),headingLine=String(md).match(/^#\s+(.*)$/m),markdownTitle=headingLine?headingLine[1].trim():"";
 if(/^Day\s*\d+/i.test(markdownTitle)){course.markdownTitle=markdownTitle;course.title=markdownTitle;course.topic=markdownTitle.replace(/^Day\s*\d+\s*[|:—-]\s*/i,"").trim()}
 const ss=sections(md),c=getContent(md,ss);c.sections=ss;current=course;state=readState(course);const topic=englishTopic(course),day=dayLabel(course),week=dayWeek(course.day);
 set("heroDay",day);set("heroTopic",topic.toUpperCase());const heroDuration=(String(c.practice||"").match(/\b\d+\s*[-–]?\s*(?:minutes?|hours?|minute|hour)\b/i)||[])[0];set("heroDuration",heroDuration?heroDuration.replace(/[-–]\s*(?=minutes?|hours?)/i," ").replace(/minutes?/i,"min").replace(/hours?/i,"hr"):"Focused session");set("dayProgressLabel",day+" PROGRESS");set("breadcrumbWeek","WEEK "+String(week).padStart(2,"0"));set("breadcrumbDay",day);set("profileWeek","Week "+String(week).padStart(2,"0")+" · Beginner");document.title="UX Daily Lab — "+topic;
 const lead="A focused introduction to "+topic+".";set("heroLead",lead);const heroZh=el("heroLeadZh");if(heroZh){heroZh.textContent="";heroZh.hidden=true}set("heroNote","What can "+topic.toLowerCase()+" help users do?");
 const intro=el("learnIntro");if(intro)intro.textContent="Build a clear mental model, then apply it in context.";
 const researchTitle=el("researchSourceTitle");if(researchTitle&&researchTitle.firstChild)researchTitle.firstChild.textContent="Explore the "+topic+" brief";set("englishSourceText","Loaded from today's course source.");
 el("learnContent").innerHTML=renderLearn(course,ss);const rs=el("researchSource");if(rs)rs.innerHTML=renderMd(md);const v=vocab(md);el("vocabContent").innerHTML=v.cards.join("")||'<p class="inline-notice">UX vocabulary is not available yet.</p>';const ph=el("phraseContent");if(ph)ph.innerHTML=v.phrases.join("");
 const challenge=el("challengeContent");if(challenge){challenge.innerHTML=renderChallenge(course,c);const session=getLegacy(ss).session,duration=(String(c.practice||"").match(/\b\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||String(c.challenge||"").match(/\b\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||session&&session.heading.match(/\d+\s*[-–]?\s*(?:minutes?|hours?)\b/i)||[])[0]||"";(()=>{const box=el("challengeTime");if(box){const node=[...box.childNodes].find(n=>n.nodeType===3);if(node)node.textContent=" "+(duration?duration+" · from the course":"See the Practice section")}})()}
 el("practiceContent").innerHTML=renderMd(c.practice||md);set("practiceFilename",course.path.split("/").pop());set("practiceSourceLabel",course.day===1?"LIVE IN-DASHBOARD PREVIEW · ORIGINAL FILE":"LIVE IN-DASHBOARD PREVIEW · MARKDOWN COURSE");
 const review=el("reviewPrompt"),reviewTitle=el("reviewPromptTitle"),reviewBody=String(c.review||"");if(reviewBody){const rq=(reviewBody.match(/(?:Reflection question|Reflection prompt)[:：]\s*["“]?([^"”\n]+)/i)||[])[1];review.textContent=rq?rq.trim():txtFirst(reviewBody);if(reviewTitle)reviewTitle.textContent="Reflection prompt"}else if(course.day!==1){review.textContent="What is one insight from today’s lesson that could change a UX decision?";if(reviewTitle)reviewTitle.textContent="One question to take with you"}const reviewIntro=el("reviewIntro");if(reviewIntro)reviewIntro.textContent="A short reflection helps you consolidate today’s learning.";sync();
}
function sync(){
 document.querySelectorAll("[data-complete-module]").forEach(b=>{const k=b.dataset.completeModule,done=state[k]===true;b.classList.toggle("is-done",done);b.setAttribute("aria-pressed",String(done));const label=b.querySelector(".module-label,.state-text");if(label)label.textContent=done?LABELS[k]+" Completed":k==="review"?"Complete Review":"Mark "+LABELS[k]+" Complete";const check=b.querySelector(".module-check,.check");if(check)check.innerHTML=done?'<svg width="12" height="12" class="ui-icon" viewBox="0 0 18 18" aria-hidden="true"><path d="m3.5 9.2 3.4 3.4 7.6-7.5"/></svg>':'<svg width="12" height="12" class="ui-icon" viewBox="0 0 18 18" aria-hidden="true"><circle cx="9" cy="9" r="5.5"/></svg>'});
 const n=MODULES.filter(k=>state[k]).length;set("progressPercent",n*20+"%");el("progressBar").style.width=n*20+"%";set("progressCopy",n+" of 5 Day "+String(current&&current.day||1).padStart(2,"0")+" modules complete");const w=current?dayWeek(current.day):0,items=courses.filter(c=>c.week===w);set("weeklyProgressCopy",items.filter(isDone).length+" / "+items.length+" lessons complete");const input=el("reflectionInput");if(input&&input.value!==state.reflection)input.value=state.reflection;const saved=el("reflectionSaved");if(saved)saved.textContent=state.reflection?"Reflection saved in this browser":"Saved in this browser";buildNav()
}
function save(){if(!current)return;try{localStorage.setItem(key(current.day),JSON.stringify(state))}catch(_){}sync()}
function showLoadError(message){const s=el("courseStatus");if(s){s.hidden=false;s.classList.add("is-error");s.textContent=message}el("learnContent").innerHTML='<p class="inline-notice">'+safe(message)+'</p>';el("vocabContent").innerHTML='<p class="inline-notice">'+safe(message)+'</p>';el("challengeContent").innerHTML='<div class="inline-notice">'+safe(message)+'</div>';el("practiceContent").innerHTML='<p class="inline-notice">'+safe(message)+'</p>'}
async function selectCourse(c){
 current=c;const s=el("courseStatus");if(s){s.hidden=false;s.classList.remove("is-error");s.textContent="Loading course…"}buildNav();
 const url=mdUrl(c.path);let response;
 try{response=await fetch(url,{cache:"no-cache"})}
 catch(error){console.error("Course Markdown fetch failed",{url,status:"network error"});showLoadError("Unable to load this course. Please try again.");return}
 if(!response.ok){console.error("Course Markdown fetch failed",{url,status:response.status});showLoadError("Unable to load this course. Please try again.");return}
 try{const markdown=await response.text();render(c,markdown);if(s)s.hidden=true}
 catch(error){console.error("Course Markdown parser failed",{url,status:response.status,message:String(error&&error.message||"Unknown render error")});showLoadError("Unable to render this course. Check the browser console for details.")}
}
function noCourse(){current=null;state=blank();buildNav();const s=el("courseStatus");if(s){s.hidden=false;s.classList.remove("is-error");s.textContent=courses.length?"Today’s course is not available yet. Choose an available lesson from the Learning Path.":"No generated courses are listed yet.";}["learnContent","vocabContent","practiceContent"].forEach(id=>el(id).innerHTML='<p class="inline-notice">Course not generated yet.</p>');el("challengeContent").innerHTML='<div class="inline-notice">Course not generated yet.</div>';el("phraseContent").innerHTML="";sync()}
function initial(){const ready=courses.filter(c=>c.available);if(!ready.length)return null;const today=cnDate(),same=ready.find(c=>c.scheduled_date===today);if(same)return same;const past=ready.filter(c=>c.scheduled_date&&c.scheduled_date<=today).sort((a,b)=>b.scheduled_date.localeCompare(a.scheduled_date)||b.day-a.day);return past[0]||ready.slice().sort((a,b)=>b.day-a.day)[0]}

async function init(){const s=el("courseStatus");try{const r=await fetch("./content/manifest.json",{cache:"no-cache"});if(!r.ok)throw Error();courses=flatten(await r.json());try{const p=await fetch("./config/learning-plan.json",{cache:"no-cache"});if(p.ok){const plan=await p.json(),items=(plan.weeks||[]).flatMap(w=>Array.isArray(w.days)?w.days:[]);courses=courses.map(c=>{const source=items.find(x=>x.project_item_id&&x.project_item_id===c.project_item_id)||items.find(x=>Number(x.day)===c.day);return source?{...c,scheduled_date:c.scheduled_date||String(source.scheduled_date||""),project_status:c.project_status||source.status}:c})}}catch(_){}buildNav();const c=initial();if(c)await selectCourse(c);else noCourse()}catch(_){showLoadError("Unable to load the course index or Markdown file.")}}
document.addEventListener("click",e=>{const b=e.target.closest("[data-complete-module]");if(!b||!current)return;const k=b.dataset.completeModule;state[k]=!state[k];save();const t=el("toast");t.textContent=LABELS[k]+(state[k]?" completed":" marked incomplete");t.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>t.classList.remove("show"),2300)});
el("reflectionInput").addEventListener("input",e=>{state.reflection=e.target.value;save()});
el("dialogOk").addEventListener("click",()=>el("upcomingDialog").close());
const rail=document.querySelector(".rail"),toggle=el("menuToggle");toggle.addEventListener("click",()=>{const open=rail.classList.toggle("open");toggle.setAttribute("aria-expanded",String(open))});document.addEventListener("click",e=>{if(rail.classList.contains("open")&&!rail.contains(e.target)&&!toggle.contains(e.target))closeNav()});document.querySelectorAll("a[href^='#']").forEach(a=>a.addEventListener("click",closeNav));
const links=[...document.querySelectorAll(".section-nav a")];if("IntersectionObserver"in window){const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting)links.forEach(a=>a.classList.toggle("active",a.hash==="#"+entry.target.id))}),{rootMargin:"-25% 0px -65% 0px"});document.querySelectorAll(".lesson-section").forEach(s=>observer.observe(s))}
init();
})();
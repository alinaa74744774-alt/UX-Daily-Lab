(() => {
  "use strict";
  const owner = "alinaa74744774-alt";
  const repo = "UX-Daily-Lab";
  const sourcePath = "Day01_User_Research_Interview_Plan.md";
  const issueUrl = `https://api.github.com/repos/${owner}/${repo}/issues/1`;
  const planUrl = `https://raw.githubusercontent.com/${owner}/${repo}/main/${sourcePath}`;
  const days = [
    ["01","User Research","用户研究","Active"],
    ["02","User Persona","用户画像","Upcoming"],
    ["03","Information Architecture","信息架构","Upcoming"],
    ["04","User Flow","用户流程","Upcoming"],
    ["05","UI Design","界面设计","Upcoming"],
    ["06","Interactive Prototype","交互原型","Upcoming"],
    ["07","Weekly Review","每周复盘","Locked"]
  ];
  const nav = document.getElementById("weekNav");
  nav.innerHTML = days.map((d,i) => `<a class="day-link ${i===0?"active":""}" href="${i===0?"#top":"#weeklyProgress"}" ${i===0?'aria-current="page"':i===6?'aria-disabled="true"':''}><span class="day-num">${d[0]}</span><span class="day-title">${d[1]}<small>${d[2]}</small></span><span class="day-status" title="${d[3]}">${i===0?"●":i===6?"◌":"↗"}</span></a>`).join("");
  nav.insertAdjacentHTML("beforeend",'<div class="week-note" id="weeklyProgress">WEEK 01 <span>1 active · 6 upcoming</span></div>');

  const escapeHtml = (s) => s.replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const inline = (s) => escapeHtml(s)
    .replace(/`([^`]+)`/g,"<code>$1</code>")
    .replace(/**([^*]+)**/g,"<strong>$1</strong>")
    .replace(/*([^*]+)*/g,"<em>$1</em>")
    .replace(/\[([^\]]+)\]\((https?:[^)]+)\)/g,'<a href="$2" target="_blank" rel="noreferrer">$1</a>');
  function renderMarkdown(markdown) {
    const lines = markdown.replace(/\r/g,"").split("\n");
    let out="", list="", table=false, quote=false;
    const closeList=()=>{if(list){out+=`</${list}>`;list="";}};
    const closeTable=()=>{if(table){out+="</tbody></table>";table=false;}};
    const closeQuote=()=>{if(quote){out+="</blockquote>";quote=false;}};
    for(let i=0;i<lines.length;i++){
      const raw=lines[i], line=raw.trim();
      if(!line){closeList();closeTable();closeQuote();continue;}
      if(/^\|.*\|$/.test(line)){
        closeList();closeQuote();
        const cells=line.slice(1,-1).split("|").map(x=>x.trim());
        if(cells.every(x=>/^:?-{3,}:?$/.test(x)))continue;
        if(!table){out+="<table><thead><tr>"+cells.map(x=>`<th>${inline(x)}</th>`).join("")+"</tr></thead><tbody>";table=true;}
        else out+="<tr>"+cells.map(x=>`<td>${inline(x)}</td>`).join("")+"</tr>";
        continue;
      }
      closeTable();
      if(/^#{1,4}\s/.test(line)){closeList();closeQuote();const m=line.match(/^(#{1,4})\s+(.*)$/);const n=m[1].length;out+=`<h${n}>${inline(m[2])}</h${n}>`;continue;}
      if(/^---+$/.test(line)){closeList();closeQuote();out+="<hr>";continue;}
      if(/^>\s?/.test(line)){closeList();if(!quote){out+="<blockquote>";quote=true;}out+=`<p>${inline(line.replace(/^>\s?/,""))}</p>`;continue;}else closeQuote();
      const ul=line.match(/^[-*]\s+(.*)$/), ol=line.match(/^\d+\.\s+(.*)$/);
      if(ul||ol){const type=ul?"ul":"ol";if(list!==type){closeList();out+=`<${type}>`;list=type;}out+=`<li>${inline((ul||ol)[1])}</li>`;continue;}
      closeList();
      if(/^<\//.test(line)||/^<!--/.test(line))continue;
      out+=`<p>${inline(line)}</p>`;
    }
    closeList();closeTable();closeQuote();
    return out;
  }
  function extractSection(md, heading) {
    const lines=md.split("\n"), start=lines.findIndex(x=>x.trim()===heading);
    if(start<0)return "";
    let end=start+1;
    while(end<lines.length&&!/^##\s/.test(lines[end]))end++;
    return lines.slice(start+1,end).join("\n").trim();
  }
  function extractSubsection(md, heading) {
    const lines=md.split("\n"), start=lines.findIndex(x=>x.trim()===heading);
    if(start<0)return "";
    let end=start+1;
    while(end<lines.length&&!/^##\s/.test(lines[end]))end++;
    return lines.slice(start+1,end).join("\n").trim();
  }
  function parseVocab(md) {
    const section=extractSection(md,"## UX English Learning｜UX 专业英语学习");
    const items=[...section.matchAll(/^###\s+\d+\.\s+(.+)$/gm)];
    return items.map((m,i)=>{
      const start=m.index+m[0].length, next=items[i+1]?.index ?? section.length;
      const body=section.slice(start,next);
      const grab=(label)=>{const re=new RegExp("- \\*\\*"+label+"[^*]*\\*\\*：?\\s*(.+)");return body.match(re)?.[1]?.trim()||"";};
      const definition=grab("英文释义 English definition");
      const chinese=grab("中文解释 Chinese explanation");
      const example=grab("UX 场景例句 UX example");
      const translation=grab("例句翻译 Translation");
      const title=m[1].replace(/（([^）]+)）/,"<span>$1</span>").replace(/\*\*/g,"");
      return `<article class="vocab-card"><div class="vocab-title"><span class="vocab-index">0${i+1}</span><h3>${title}</h3></div><p class="vocab-def">${escapeHtml(definition)}</p><p class="vocab-zh">${escapeHtml(chinese)}</p><div class="vocab-example">“${escapeHtml(example.replace(/^“|”$/g,""))}”</div><div class="vocab-translation">${escapeHtml(translation)}</div></article>`;
    }).join("");
  }
  function markedSection(text, start, end) {
    const a=text.indexOf(start), b=end?text.indexOf(end,a+start.length):-1;
    return a<0?"":text.slice(a+start.length,b<0?undefined:b).trim();
  }
  const status = JSON.parse(localStorage.getItem("uxdl-day01-status")||'{"learning":false,"practice":false}');
  const learningBtn=document.getElementById("learningDone"), practiceBtn=document.getElementById("practiceDone");
  const toast=document.getElementById("toast");
  let toastTimer;
  function notify(message){toast.textContent=message;toast.classList.add("show");clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.classList.remove("show"),2200);}
  function save(){localStorage.setItem("uxdl-day01-status",JSON.stringify(status));syncStatus();}
  function syncStatus(){
    learningBtn.classList.toggle("is-done",status.learning);learningBtn.setAttribute("aria-pressed",String(status.learning));
    learningBtn.querySelector(".review-text").innerHTML=`<b>Learning Completed</b><small>${status.learning?"今日学习已完成 · Saved on this device":"标记今日学习已完成"}</small>`;
    learningBtn.querySelector(".review-check").textContent=status.learning?"✓":"○";
    practiceBtn.classList.toggle("is-done",status.practice);practiceBtn.setAttribute("aria-pressed",String(status.practice));
    practiceBtn.querySelector(".state-text").textContent=status.practice?"Practice completed":"Mark practice complete";
    document.getElementById("practiceStatus").textContent=status.practice?"COMPLETED":"IN PROGRESS";
    document.getElementById("practiceStatusIcon").textContent=status.practice?"✓":"○";
    document.getElementById("practiceStatusText").textContent=status.practice?"Day 01 deliverable marked complete":"完成 Day 01 访谈计划后标记";
    const done=Number(status.learning)+Number(status.practice),pct=Math.round(done/2*100);
    document.getElementById("progressPercent").textContent=pct+"%";
    document.getElementById("progressBar").style.width=pct+"%";
    document.getElementById("progressCopy").textContent=done===2?"Day 01 complete — great work.":done===1?"One more step to complete Day 01.":"One small step today.";
  }
  learningBtn.addEventListener("click",()=>{status.learning=!status.learning;save();notify(status.learning?"Learning progress saved":"Learning status reset");});
  practiceBtn.addEventListener("click",()=>{status.practice=!status.practice;save();notify(status.practice?"Practice progress saved":"Practice status reset");});
  syncStatus();

  const menu=document.querySelector(".rail"), toggle=document.getElementById("menuToggle");
  toggle.addEventListener("click",()=>menu.classList.toggle("open"));
  menu.querySelectorAll("a").forEach(a=>a.addEventListener("click",()=>menu.classList.remove("open")));
  const sectionLinks=[...document.querySelectorAll(".section-nav a")];
  const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){sectionLinks.forEach(a=>a.classList.toggle("active",a.hash==="#"+entry.target.id));}}),{rootMargin:"-25% 0px -65% 0px"});
  document.querySelectorAll(".lesson-section").forEach(s=>observer.observe(s));

  fetch(planUrl).then(r=>{if(!r.ok)throw Error("Could not load the Day 01 file.");return r.text();}).then(md=>{
    const goal=extractSection(md,"## Research Goal｜研究目标");
    const method=extractSection(md,"## Research Method｜研究方法");
    const target=extractSection(md,"## Target User｜目标用户");
    document.getElementById("researchSource").innerHTML=renderMarkdown(["## Research Goal｜研究目标",goal,"## Research Method｜研究方法",method,"## Target User｜目标用户",target].join("\n\n"));
    const vocab=parseVocab(md);
    if(vocab)document.getElementById("vocabContent").innerHTML=vocab;
    document.getElementById("practiceContent").innerHTML=renderMarkdown(md);
  }).catch(()=>{
    document.getElementById("researchSource").innerHTML='<p>Could not load the original file. <a href="./Day01_User_Research_Interview_Plan.md">Open it directly</a>.</p>';
    document.getElementById("practiceContent").innerHTML='<p>Could not load the original file. <a href="./Day01_User_Research_Interview_Plan.md">Open it directly</a>.</p>';
    document.getElementById("vocabContent").innerHTML='<div class="vocab-card">Vocabulary is available in the <a href="./Day01_User_Research_Interview_Plan.md">Day 01 source file</a>.</div>';
  });
  fetch(issueUrl,{headers:{Accept:"application/vnd.github+json"}}).then(r=>{if(!r.ok)throw Error("Task unavailable");return r.json();}).then(issue=>{
    const marked=markedSection(issue.body||"","<!-- ux-english-challenge:day-01:start -->","<!-- ux-english-challenge:day-01:end -->");
    const task=extractSubsection(marked,"## Daily UX Challenge");
    if(task)document.getElementById("challengeSource").innerHTML=renderMarkdown(task);
  }).catch(()=>{document.getElementById("challengeSource").innerHTML='<p>Task details are temporarily unavailable. <a href="https://github.com/alinaa74744774-alt/UX-Daily-Lab/issues/1" target="_blank" rel="noreferrer">Open GitHub Issue #1</a>.</p>';});
})();
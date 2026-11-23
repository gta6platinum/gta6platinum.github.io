const {JSDOM}=require(require('child_process').execSync('npm root -g').toString().trim()+'/jsdom');
const fs=require('fs');const s=fs.readFileSync(process.argv[2],'utf8');
for(const L of ['en','ar','es']){
 const d=new JSDOM(s,{runScripts:'dangerously',url:'https://x.test/',beforeParse(w){w.localStorage.setItem('gta6lang',L);w.scrollTo=()=>{};w.HTMLElement.prototype.scrollIntoView=()=>{}}});
 const w=d.window;const errs=[];w.addEventListener('error',e=>errs.push(e.message));
 const left=new Set();
 ['ch2','more','cards','wink','med','trophy','weap','cars','garage','full','codes','sum'].forEach(t=>{const b=w.document.querySelector('[data-tab='+t+']');if(!b)return;b.click();if(t==='map')w.document.querySelector('[data-town=pg]').dispatchEvent(new w.MouseEvent('click',{bubbles:true}));
  if(L!=='en'){const it=w.document.createTreeWalker(w.document.querySelector('main'),4);let n;while(n=it.nextNode()){const v=n.nodeValue.trim();if(/^[A-Z][a-z]+ [a-z]+ [a-z]+/.test(v)&&v.length>25)left.add(v.slice(0,80))}}});
 console.log(L,'dir',w.document.documentElement.dir,'h1',w.document.querySelector('h1').textContent,'|',w.document.getElementById('ptxt').textContent,'| errs',errs.length, '| leftover',left.size);
 if(L==='es')[...left].slice(0,70).forEach(x=>console.log('   ',x));
}

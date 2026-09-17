const fs = require('fs');
const file = process.argv[2];
const html = fs.readFileSync(file, 'utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];

// ---- 极简 DOM shim：只实现本页脚本用到的接口 ----
function El(tag){ this.attrs = {}; this.classes = new Set(); this.children = []; this.textContent = ''; }
El.prototype.setAttribute = function(k, v){ this.attrs[k] = v; };
El.prototype.getAttribute = function(k){ return k in this.attrs ? this.attrs[k] : null; };
El.prototype.closest = function(sel){ let n = this; const cls = sel.replace('.', ''); while(n){ if(n.classes.has(cls)) return n; n = n.parent; } return null; };
El.prototype.matches = function(sel){ return sel.split('.').filter(Boolean).every(c => this.classes.has(c)); };
El.prototype.descendants = function(){ let out = []; for(const c of this.children){ out.push(c); out = out.concat(c.descendants()); } return out; };
El.prototype.querySelectorAll = function(selStr){
  const parts = selStr.trim().split(/\s+/);
  const leaf = parts[parts.length - 1].replace(/^[.#]/, '');
  return this.descendants().filter(el => {
    if(!el.matches(leaf)) return false;
    if(parts.length === 1) return true;
    const anc = parts[0].replace(/^[.#]/, '');
    let n = el.parent;
    while(n){ if(n.matches(anc)) return true; n = n.parent; }
    return false;
  });
};
El.prototype.querySelector = function(selStr){ return this.querySelectorAll(selStr)[0]; };
El.prototype.addEventListener = function(type, fn){ (this._h = this._h || {})[type] = fn; };
El.prototype.click = function(){ if(this._h && this._h.click) this._h.click(); };
Object.defineProperty(El.prototype, 'classList', { get(){ const self = this; return {
  add: (...c) => c.forEach(x => self.classes.add(x)),
  remove: (...c) => c.forEach(x => self.classes.delete(x)),
  contains: c => self.classes.has(c) }; } });
Object.defineProperty(El.prototype, 'className', { get(){ return [...this.classes].join(' '); }, set(v){ this.classes = new Set(String(v).split(/\s+/).filter(Boolean)); } });
const root = new El('root');

// 用正则切出每个 quiz 卡片内的事件元素
const blocks = [...html.matchAll(/<div class="quiz" data-ans="([^"]*)">([\s\S]*?)<div class="src">([\s\S]*?)<\/div>/g)];
for(const b of blocks){
  const card = new El('div'); card.classes = new Set(['quiz']); card.parent = root; root.children.push(card);
  card.setAttribute('data-ans', b[1]);
  const body = b[2];
  // 逐行扫描 div/button 起止，构造扁平结构（opt/fb 都是 card 的直接子元素）
  const re = /<(div|button)\b([^>]*?)(\/?)>/g; let m;
  while((m = re.exec(body))){
    const attrs = m[2];
    const el = new El(m[1]); el.parent = card; card.children.push(el);
    const cm = /class="([^"]*)"/.exec(attrs); if(cm) el.classes = new Set(cm[1].split(/\s+/).filter(Boolean));
    const da = /data-(ans|v|ok)="([^"]*)"/g; let d;
    while((d = da.exec(attrs))) el.setAttribute('data-' + d[1], d[2]);
  }
  const src = new El('div'); src.classes = new Set(['src']); src.parent = card; card.children.push(src);
  src.textContent = b[3];
}

function sel(selStr){
  const parts = selStr.trim().split(/\s+/);
  const leaf = parts[parts.length - 1].replace(/^[.#]/, '');
  return root.descendants().filter(el => {
    if(!el.matches(leaf)) return false;
    if(parts.length === 1) return true;
    const anc = parts[0].replace(/^[.#]/, '');
    let n = el.parent;
    while(n){ if(n.matches(anc)) return true; n = n.parent; }
    return false;
  });
}
const scoreEl = new El('div'); scoreEl.classes = new Set(['score']);
const doc = { querySelectorAll: sel, getElementById: () => scoreEl };

const api = new Function('document', 'window', script + '\nreturn {gradeQuiz,revealQuiz,resetQuiz};')(doc, {});
const cards = sel('.quiz');
console.log('题量:', cards.length);
console.log('难度分布: 入门', (html.match(/lv lv-e/g)||[]).length, '/ 进阶', (html.match(/lv lv-m/g)||[]).length, '/ 挑战', (html.match(/lv lv-h/g)||[]).length);

const keys = cards.map(c => c.getAttribute('data-ans'));
function run(pick){
  api.resetQuiz();
  cards.forEach((card, i) => {
    const opts = card.children.filter(e => e.classes.has('opt'));
    const v = pick(i, opts);
    const target = opts.find(b => b.getAttribute('data-v') === v);
    if(target) target.click();          // 走真实的点击处理器
  });
  api.gradeQuiz();
  return scoreEl.textContent;
}
console.log('全选对 ->', run((i, o) => keys[i]));
console.log('全选错 ->', run((i, o) => o.map(b => b.getAttribute('data-v')).find(v => v !== keys[i])));
console.log('仅第 1 题错 ->', run((i, o) => i === 0 ? o.map(b => b.getAttribute('data-v')).find(v => v !== keys[i]) : keys[i]));
console.log('未作答 ->', run((i, o) => 'Z'));

const bad = [];
cards.forEach((c, i) => {
  const vs = c.children.filter(e => e.classes.has('opt')).map(b => b.getAttribute('data-v'));
  if(vs.indexOf(c.getAttribute('data-ans')) < 0) bad.push('Q' + (i + 1) + ' 答案不在选项中');
  if(vs.length !== 4) bad.push('Q' + (i + 1) + ' 选项数不是 4');
  const fb = c.children.find(e => e.classes.has('fb'));
  if(!fb || !fb.getAttribute('data-ok')) bad.push('Q' + (i + 1) + ' 缺 data-ok 反馈');
  const src = c.children.find(e => e.classes.has('src'));
  if(!src || !/来源/.test(src.textContent)) bad.push('Q' + (i + 1) + ' 缺来源标注');
});
console.log('结构校验:', bad.length ? bad.join('; ') : '通过');
console.log('答案键:', keys.join(' / '));

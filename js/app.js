// Screens and interaction. Each role has a home screen; the ANC card and
// the registration form are separate pages reached from the ASHA or doctor view.

const main = document.getElementById('main');
const UI = { page: 'home', pid: null, visitId: null, flash: null };

function go(page, opts = {}) {
  Object.assign(UI, { page, pid: null, visitId: null, flash: null }, opts);
  render();
  window.scrollTo(0, 0);
}

/* ---------- small helpers ---------- */
const name = m => esc(L(m.name));
const village = key => t('v_' + key);
const status = k => `<span class="st st-${k}">${t('s_' + k)}</span>`;
const stats = items => `<p class="stats">${items.map(([n, key, cls]) =>
  `<span class="${cls || ''}"><b>${n}</b>${t(key)}</span>`).join('')}</p>`;
const table = (heads, rows) => `<div class="tw"><table><thead><tr>${heads.map(h =>
  `<th class="${h.startsWith('>') ? 'right' : ''}">${t(h.replace('>', ''))}</th>`).join('')}</tr></thead><tbody>${rows.join('')}</tbody></table></div>`;
const opSymbol = op => (op === '>=' ? '≥' : op);
const pct = (a, b) => (b ? Math.round((a / b) * 100) : 0);

// "BP 146/94 · Hb 10.9 g/dL · 59 kg" with any reading that tripped a rule in red
function readings(v, hits = []) {
  if (!v || !v.actualDate) return '';
  const bad = (...params) => hits.some(h => params.includes(h.param));
  const wrap = (val, ...params) => (bad(...params) ? `<span class="bad">${val}</span>` : val);
  return t('reads', { bp: '§bp', hb: '§hb', wt: v.weight ?? '—' })
    .replace('§bp', wrap(`${v.bpSys}/${v.bpDia}`, 'bpSys', 'bpDia'))
    .replace('§hb', wrap(v.hb, 'hb'));
}

/* ---------- render ---------- */
function render() {
  document.documentElement.lang = LANG;
  document.title = STRINGS[LANG].appName;
  document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = STRINGS[LANG][el.dataset.i18n]; });
  const langBtn = document.getElementById('lang');
  langBtn.textContent = LANG === 'en' ? 'ગુજરાતી' : 'English';
  langBtn.lang = LANG === 'en' ? 'gu' : 'en';
  document.querySelectorAll('#nav button').forEach(b => b.classList.toggle('on', b.dataset.role === S.role));

  if (UI.page === 'card') return renderCard();
  if (UI.page === 'register') return renderRegister();
  ({ asha: renderAsha, doctor: renderDoctor, admin: renderAdmin, sms: renderSms })[S.role]();
}

/* ---------- ASHA worker ---------- */
function renderAsha() {
  const me = userById(S.me.asha);
  const pregs = activePregnancies().filter(p => motherOf(p).ashaId === me.id);
  const pending = pregs
    .flatMap(p => visitsOf(p).filter(v => ['due', 'missed'].includes(visitStatus(v))).map(v => ({ p, v })))
    .sort((a, b) => a.v.scheduledDate - b.v.scheduledDate);

  main.innerHTML = `
    <div class="head">
      <div><h1>${t('hello', { name: firstName(me.name) })}</h1><p class="sub">${village(me.village)} · ${esc(fmt(TODAY))}</p></div>
      <button class="btn" data-go="register">${t('btnRegister')}</button>
    </div>
    ${stats([
      [pregs.length, 'statMothers'],
      [pending.filter(x => visitStatus(x.v) === 'due').length, 'statDue'],
      [pending.filter(x => visitStatus(x.v) === 'missed').length, 'statMissed', 'mod'],
      [pregs.filter(p => assess(p).level === 'high').length, 'statHigh', 'high']
    ])}

    <h2>${t('hNeeds')}</h2>
    <p class="sub">${t('subNeeds')}</p>
    ${pending.length ? table(['colName', 'colVisit', 'colScheduled', 'colStatus', '>'], pending.map(({ p, v }) => `
      <tr>
        <td><button class="link" data-open="${p.id}">${name(motherOf(p))}</button></td>
        <td>${t('anc', { n: v.no })}</td>
        <td class="n">${esc(fmtShort(v.scheduledDate))}</td>
        <td>${status(visitStatus(v))}</td>
        <td class="right"><button class="link" data-rec="${v.id}">${t('record')}</button></td>
      </tr>`)) : `<p class="empty">${t('noneNeeds')}</p>`}

    <h2>${t('hMyMothers')}</h2>
    ${table(['colName', 'colVillage', 'colWeek', 'colEdd', 'colNext', 'colRisk'], pregs.map(p => {
      const m = motherOf(p), n = nextVisit(p);
      return `<tr>
        <td><button class="link" data-open="${p.id}">${name(m)}</button></td>
        <td>${village(m.village)}</td>
        <td class="n">${gestationalWeek(p)}</td>
        <td class="n">${esc(fmtShort(p.edd))}</td>
        <td class="n">${n ? `${esc(fmtShort(n.scheduledDate))} ${visitStatus(n) === 'missed' ? status('missed') : ''}` : t('allDone')}</td>
        <td>${status(assess(p).level)}</td>
      </tr>`;
    }))}`;
}

/* ---------- ANC card (one pregnancy) ---------- */
function renderCard() {
  const p = S.pregnancies.find(x => x.id === UI.pid);
  const m = motherOf(p), a = assess(p), vs = visitsOf(p);
  const recVisit = UI.visitId ? vs.find(v => v.id === UI.visitId) : null;
  const isAsha = S.role === 'asha';

  const flash = UI.flash ? `<p class="flash ${UI.flash}">${t('res' + UI.flash[0].toUpperCase() + UI.flash.slice(1), { doc: userById(S.me.doctor).name })}</p>` : '';

  main.innerHTML = `
    <button class="link back" data-go="home">${t('back')}</button>
    <h1>${name(m)}</h1>
    <p class="sub">${village(m.village)} · ${t('yrs', { n: m.age })} · ${t('fAsha')}: ${esc(L(userById(m.ashaId).name))}</p>
    ${flash}

    <dl class="facts">
      <div><dt>${t('fPhone')}</dt><dd class="n">${esc(m.phone)}</dd></div>
      <div><dt>${t('fBlood')}</dt><dd>${m.bloodGroup === 'Unknown' ? t('unknown') : esc(m.bloodGroup)}</dd></div>
      <div><dt>${t('fGP')}</dt><dd>G${p.gravida} P${p.parity}</dd></div>
      <div><dt>${t('fLmp')}</dt><dd class="n">${esc(fmt(p.lmp))}</dd></div>
      <div><dt>${t('fEdd')}</dt><dd class="n">${esc(fmt(p.edd))}</dd></div>
      <div><dt>${t('fWeek')}</dt><dd class="n">${gestationalWeek(p)}</dd></div>
    </dl>
    <p class="risk">${t('riskLabel')} ${status(a.level)}${a.reasons.length ? ` · ${a.reasons.map(r => t(r)).join(', ')}` : ''}</p>

    ${recVisit ? recordForm(recVisit, p) : ''}

    <h2>${t('hVisits')}</h2>
    ${table(['colVisit', 'colScheduled', 'colStatus', 'colReadings', ...(isAsha ? ['>'] : [])], vs.map(v => {
      const st = visitStatus(v);
      return `<tr>
        <td>${t('anc', { n: v.no })}</td>
        <td class="n">${esc(fmtShort(v.scheduledDate))}</td>
        <td>${status(st)}</td>
        <td>${readings(v, v === a.last ? a.hits : [])}${v.notes ? `<div class="sub">${esc(L(v.notes))}</div>` : ''}</td>
        ${isAsha ? `<td class="right">${st !== 'done' && v.id !== UI.visitId ? `<button class="link" data-rec="${v.id}">${t('record')}</button>` : ''}</td>` : ''}
      </tr>`;
    }))}

    ${p.notes.length ? `<h2>${t('hNotes')}</h2>${p.notes.map(n => `
      <div class="dnote"><small>${esc(L(userById(n.by).name))} · ${esc(fmt(n.at))} · ${t(n.decision)}</small>${esc(L(n.text))}</div>`).join('')}` : ''}`;

  main.querySelector('#f-wt')?.focus();
}

function recordForm(v, p) {
  return `
  <div class="recbox">
    <h2>${t('hRecord', { n: v.no })}</h2>
    <p class="sub">${t('recSub', { date: TODAY, w: gestationalWeek(p) })}</p>
    <form class="f" id="recform" data-visit="${v.id}">
      <label class="fld">${t('lSys')}<input id="f-sys" type="number" required min="60" max="250" value="118"></label>
      <label class="fld">${t('lDia')}<input id="f-dia" type="number" required min="30" max="160" value="76"></label>
      <label class="fld">${t('lHb')}<input id="f-hb" type="number" required step="0.1" min="2" max="20" value="11"></label>
      <label class="fld">${t('lWt')}<input id="f-wt" type="number" required step="0.1" min="25" max="150"></label>
      <label class="fld full">${t('lNotes')}<textarea id="f-notes" rows="2" placeholder="${t('phNotes')}"></textarea></label>
      <div class="full actions">
        <button class="btn" type="submit">${t('saveVisit')}</button>
        <button class="link" type="button" data-cancel>${t('cancel')}</button>
      </div>
    </form>
  </div>`;
}

/* ---------- registration ---------- */
function renderRegister() {
  const iso = d => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
  const bloodGroups = ['Unknown', 'A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'];
  main.innerHTML = `
    <button class="link back" data-go="home">${t('back')}</button>
    <h1>${t('btnRegister')}</h1>
    <p class="sub">${t('regSub')}</p>
    <div id="regerr"></div>
    <form class="f" id="regform">
      <label class="fld full">${t('gName')}<input id="g-name" required value="${LANG === 'gu' ? 'આશા ઠાકોર' : 'Asha Thakor'}"></label>
      <label class="fld">${t('gAge')}<input id="g-age" type="number" required min="12" max="55" value="23"></label>
      <label class="fld">${t('gPhone')}<input id="g-phone" required pattern="[6-9][0-9]{9}" inputmode="numeric" value="9825076143"></label>
      <label class="fld">${t('gVillage')}<select id="g-village">${['bakrol', 'vadod'].map(v => `<option value="${v}">${village(v)}</option>`).join('')}</select></label>
      <label class="fld">${t('fBlood')}<select id="g-bg">${bloodGroups.map(b => `<option value="${b}">${b === 'Unknown' ? t('unknown') : b}</option>`).join('')}</select></label>
      <label class="fld">${t('fLmp')}<input id="g-lmp" type="date" required max="${iso(TODAY)}" value="${iso(addDays(TODAY, -63))}"></label>
      <div class="fld">${t('fGP')}
        <div class="pair">
          <input id="g-g" type="number" min="1" value="1" aria-label="${t('gGrav')}">
          <input id="g-p" type="number" min="0" value="0" aria-label="${t('gPara')}">
        </div>
      </div>
      <p class="note full">${t('regHint')}</p>
      <div class="full"><button class="btn" type="submit">${t('regSubmit')}</button></div>
    </form>`;
}

/* ---------- doctor ---------- */
function renderDoctor() {
  const me = userById(S.me.doctor);
  const rows = activePregnancies().map(p => ({ p, a: assess(p), m: motherOf(p) }));
  const queue = rows.filter(x => x.a.level === 'high' && !x.p.reviewed);
  const watch = rows.filter(x => x.a.level === 'moderate');
  const reviewed = rows.filter(x => x.p.notes.length);

  main.innerHTML = `
    <h1>${esc(L(me.name))}</h1>
    <p class="sub">${t('phcName')} · ${esc(fmt(TODAY))}</p>
    ${stats([
      [queue.length, 'statQueue', 'high'],
      [watch.length, 'statWatch', 'mod'],
      [reviewed.length, 'statReviewed'],
      [rows.length, 'statActive']
    ])}
    <p class="note">${t('docNote')}</p>

    <h2>${t('hQueue')}</h2>
    <p class="sub">${t('subQueue')}</p>
    ${queue.length ? queue.map(({ p, a, m }) => `
      <div class="case">
        <div class="case-top">
          <div><strong><button class="link" data-open="${p.id}">${name(m)}</button>, ${m.age}</strong>
            <div class="sub">${t('metaCase', { village: { k: 'v_' + m.village }, w: gestationalWeek(p), g: p.gravida, p: p.parity, asha: userById(m.ashaId).name })}</div></div>
          <span class="st st-high">${a.reasons.map(r => t(r)).join(', ')}</span>
        </div>
        <p class="reads">${readings(a.last, a.hits)} · ${t('lastVisit', { date: a.last.actualDate })}</p>
        <div class="review">
          <textarea id="note-${p.id}" rows="2" placeholder="${t('phDocNote')}"></textarea>
          <select id="dec-${p.id}" aria-label="${t('colDecision')}">
            ${['dRoutine', 'dPhc', 'dRefer'].map(d => `<option value="${d}">${t(d)}</option>`).join('')}
          </select>
          <button class="btn" data-review="${p.id}">${t('saveReview')}</button>
        </div>
      </div>`).join('') : `<p class="empty">${t('noneQueue')}</p>`}

    <h2>${t('hWatch')}</h2>
    <p class="sub">${t('subWatch')}</p>
    ${watch.length ? table(['colName', 'colWeek', 'colReasons', 'colReadings'], watch.map(({ p, a, m }) => `
      <tr>
        <td><button class="link" data-open="${p.id}">${name(m)}</button></td>
        <td class="n">${gestationalWeek(p)}</td>
        <td><span class="st st-moderate">${a.reasons.map(r => t(r)).join(', ')}</span></td>
        <td>${readings(a.last, a.hits)}</td>
      </tr>`)) : `<p class="empty">${t('noneWatch')}</p>`}

    <h2>${t('hReviewed')}</h2>
    ${reviewed.length ? table(['colName', 'colDate', 'colDecision', 'colNote'], reviewed.map(({ p, m }) => {
      const n = p.notes[p.notes.length - 1];
      return `<tr>
        <td><button class="link" data-open="${p.id}">${name(m)}</button></td>
        <td class="n">${esc(fmtShort(n.at))}</td>
        <td>${t(n.decision)}</td>
        <td class="wrap">${esc(L(n.text))}</td>
      </tr>`;
    })) : `<p class="empty">${t('noneReviewed')}</p>`}`;
}

/* ---------- PHC admin ---------- */
function renderAdmin() {
  const pregs = activePregnancies();
  const vs = pregs.flatMap(visitsOf);
  const done = vs.filter(v => v.actualDate).length;
  const missed = vs.filter(v => visitStatus(v) === 'missed').length;

  const byVisit = [1, 2, 3, 4].map(n => {
    const due = vs.filter(v => v.no === n && v.scheduledDate <= TODAY);
    return { n, due: due.length, done: due.filter(v => v.actualDate).length };
  });
  const byAsha = S.users.filter(u => u.role === 'asha').map(u => {
    const ps = pregs.filter(p => motherOf(p).ashaId === u.id);
    const v = ps.flatMap(visitsOf);
    const d = v.filter(x => x.actualDate).length, m = v.filter(x => visitStatus(x) === 'missed').length;
    return { u, mothers: ps.length, d, m, high: ps.filter(p => assess(p).level === 'high').length };
  });

  main.innerHTML = `
    <h1>${t('hAdmin')}</h1>
    <p class="sub">${t('adminSub', { name: userById(S.me.admin).name, date: TODAY })}</p>
    ${stats([
      [pregs.length, 'statRegistered'],
      [pct(done, done + missed) + '%', 'statOnTrack'],
      [missed, 'statMissed', 'mod'],
      [pregs.filter(p => assess(p).level === 'high').length, 'statHigh', 'high']
    ])}

    <div class="two">
      <div>
        <h2>${t('hCompletion')}</h2>
        <p class="sub">${t('subCompletion')}</p>
        ${table(['colVisit', '>colDone'], byVisit.map(b => `
          <tr>
            <td>${t('anc', { n: b.n })}<div class="bar"><i style="width:${pct(b.done, b.due)}%"></i></div></td>
            <td class="n right">${b.done} / ${b.due}</td>
          </tr>`))}
      </div>
      <div>
        <h2>${t('hByAsha')}</h2>
        <p class="sub">&nbsp;</p>
        ${table(['navAsha', '>colMothers', '>colDone', '>colMissed', '>colOnTrack', '>colHigh'], byAsha.map(a => `
          <tr>
            <td>${esc(L(a.u.name))}<div class="sub">${village(a.u.village)}</div></td>
            <td class="n right">${a.mothers}</td>
            <td class="n right">${a.d}</td>
            <td class="n right">${a.m}</td>
            <td class="n right">${pct(a.d, a.d + a.m)}%</td>
            <td class="n right">${a.high}</td>
          </tr>`))}
      </div>
    </div>

    <h2>${t('hRules')}</h2>
    <p class="sub">${t('subRules')}</p>
    <div class="rules">${table(['colReading', 'colCondition', 'colFlag', 'colShownAs'], S.rules.map(r => `
      <tr>
        <td>${t('p_' + r.param)}</td>
        <td class="n">${opSymbol(r.op)} <input type="number" step="0.1" id="rule-${r.id}" data-rule="${r.id}" value="${r.value}" aria-label="${t('p_' + r.param)}"> ${t(r.unit)}</td>
        <td>${status(r.sev)}</td>
        <td>${t(r.reason)}</td>
      </tr>`))}</div>`;
}

/* ---------- SMS log ---------- */
function renderSms() {
  const recipient = to => (to.startsWith('u') ? esc(L(userById(to).name)) : `<span class="n">${esc(to)}</span>`);
  main.innerHTML = `
    <div class="head">
      <div><h1>${t('hSms')}</h1><p class="sub">${t('subSms')}</p></div>
      <button class="btn" id="runjob">${t('runJob')}</button>
    </div>
    ${S.sms.length ? table(['colTime', 'colTo', 'colType', 'colMsg'], S.sms.map(s => `
      <tr>
        <td class="n">${esc(fmtShort(s.at))} ${esc(s.at.toLocaleTimeString(locale(), { hour: '2-digit', minute: '2-digit' }))}</td>
        <td style="white-space:nowrap">${recipient(s.to)}</td>
        <td><span class="${s.alert ? 'st st-high' : ''}" style="white-space:nowrap">${t(s.kind)}</span></td>
        <td class="wrap">${t(s.msg, s.vars)}</td>
      </tr>`)) : `<p class="empty">${t('noSms')}</p>`}`;
}

/* ---------- actions ---------- */
function registerMother() {
  const val = id => document.getElementById(id).value.trim();
  const err = html => { document.getElementById('regerr').innerHTML = `<p class="err">${html}</p>`; };
  const phone = val('g-phone');

  const existing = S.mothers.find(m => m.phone === phone && S.pregnancies.some(p => p.motherId === m.id && p.status === 'active'));
  if (existing) return err(t('errDup', { name: existing.name, phone }));

  const lmp = startOfDay(new Date(val('g-lmp') + 'T00:00'));
  if ((TODAY - lmp) / DAY > 40 * 7) return err(t('errLmp'));

  const m = { id: newId('m'), name: val('g-name'), age: +val('g-age'), phone, village: val('g-village'), bloodGroup: val('g-bg'), ashaId: S.me.asha };
  const p = { id: newId('p'), motherId: m.id, lmp, edd: addDays(lmp, 280), gravida: +val('g-g') || 1, parity: +val('g-p') || 0, status: 'active', reviewed: false, notes: [] };
  S.mothers.push(m);
  S.pregnancies.push(p);
  const schedule = generateSchedule(p);
  S.visits.push(...schedule);

  sendSms(phone, 'k_reg', 'm_reg', { name: firstName(m.name), edd: p.edd, date: schedule[0].scheduledDate });
  go('card', { pid: p.id });
  toast(t('toastReg', { name: m.name, n: schedule.length }));
}

function recordVisit(visitId) {
  const v = S.visits.find(x => x.id === visitId);
  const p = S.pregnancies.find(x => x.id === v.pregnancyId);
  const m = motherOf(p);
  const num = id => parseFloat(document.getElementById(id).value);

  Object.assign(v, {
    actualDate: TODAY, bpSys: num('f-sys'), bpDia: num('f-dia'), hb: num('f-hb'), weight: num('f-wt'),
    notes: document.getElementById('f-notes').value.trim()
  });

  const a = assess(p);
  if (a.level === 'high') {
    p.reviewed = false;
    sendSms(S.me.doctor, 'k_alert', 'm_alert', { name: m.name, village: { k: 'v_' + m.village }, w: gestationalWeek(p), reasons: a.reasons }, true);
  }
  const next = nextVisit(p);
  if (next) sendSms(m.phone, 'k_visit', 'm_visit', { name: firstName(m.name), date: next.scheduledDate });
  else sendSms(m.phone, 'k_visit', 'm_visitLast', { name: firstName(m.name) });

  go('card', { pid: p.id, flash: a.level });
}

function saveReview(pid) {
  const p = S.pregnancies.find(x => x.id === pid), m = motherOf(p);
  const note = document.getElementById('note-' + pid);
  const decision = document.getElementById('dec-' + pid).value;
  if (!note.value.trim()) { toast(t('needNote')); note.focus(); return; }

  p.notes.push({ at: TODAY, by: S.me.doctor, decision, text: note.value.trim() });
  p.reviewed = true;
  if (decision === 'dRefer') sendSms(m.phone, 'k_referral', 'm_referral', { name: firstName(m.name) });
  if (decision === 'dPhc') sendSms(m.phone, 'k_docvisit', 'm_docvisit', { name: firstName(m.name) });
  sendSms(m.ashaId, 'k_docnote', 'm_docnote', { name: m.name, decision: { k: decision }, note: note.value.trim() });

  render();
  toast(t('toastReview', { name: m.name }));
}

// Daily job: remind mothers with a visit in the next 3 days, and report newly missed visits
function runReminderJob() {
  let reminders = 0, missedNotices = 0;
  for (const p of activePregnancies()) {
    const m = motherOf(p);
    for (const v of visitsOf(p)) {
      const st = visitStatus(v);
      if (!v.actualDate && st !== 'missed' && (v.scheduledDate - TODAY) / DAY <= 3 && v.remindedOn !== +TODAY) {
        v.remindedOn = +TODAY;
        reminders++;
        sendSms(m.phone, 'k_reminder', 'm_reminder', { name: firstName(m.name), date: v.scheduledDate, village: { k: 'v_' + m.village } });
      }
      if (st === 'missed' && !v.missedNotified) {
        v.missedNotified = true;
        missedNotices++;
        sendSms(m.phone, 'k_missed', 'm_missed', { name: firstName(m.name), date: v.scheduledDate });
        sendSms(m.ashaId, 'k_missed', 'm_missedAsha', { name: m.name, n: v.no, date: v.scheduledDate });
      }
    }
  }
  render();
  toast(reminders + missedNotices ? t('toastJob', { r: reminders, m: missedNotices }) : t('toastJobNone'));
}

let toastTimer;
function toast(html) {
  const el = document.getElementById('toast');
  el.innerHTML = html;
  el.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.hidden = true; }, 3500);
}

/* ---------- events ---------- */
document.addEventListener('click', e => {
  const el = e.target.closest('button');
  if (!el) return;
  if (el.id === 'lang') { setLang(LANG === 'en' ? 'gu' : 'en'); render(); return; }
  if (el.dataset.role) { S.role = el.dataset.role; go('home'); return; }
  if (el.dataset.go) { go(el.dataset.go); return; }
  if (el.dataset.open) { go('card', { pid: el.dataset.open }); return; }
  if (el.dataset.rec) {
    const v = S.visits.find(x => x.id === el.dataset.rec);
    go('card', { pid: v.pregnancyId, visitId: v.id });
    return;
  }
  if (el.hasAttribute('data-cancel')) { go('card', { pid: UI.pid }); return; }
  if (el.dataset.review) { saveReview(el.dataset.review); return; }
  if (el.id === 'runjob') runReminderJob();
});

document.addEventListener('submit', e => {
  e.preventDefault();
  if (e.target.id === 'regform') registerMother();
  if (e.target.id === 'recform') recordVisit(e.target.dataset.visit);
});

document.addEventListener('change', e => {
  const id = e.target.dataset.rule;
  if (!id) return;
  const rule = S.rules.find(r => r.id === id);
  const value = parseFloat(e.target.value);
  if (isNaN(value)) return;
  rule.value = value;
  render();
  toast(t('toastRule', { label: { k: 'p_' + rule.param }, op: opSymbol(rule.op), n: value, unit: { k: rule.unit } }));
});

render();

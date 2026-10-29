// Frontend data adapter: fetch persistent API records and convert them to UI-friendly shapes.

const DAY = 86400000;
const startOfDay = d => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
const addDays = (d, n) => new Date(d.getTime() + n * DAY);
const TODAY = startOfDay(new Date());

// Same-origin requests let FastAPI serve both the UI and the API without a separate server.
const API_ROOT = `${window.location.origin}/api`;
const S = {
  role: 'asha',
  me: { asha: 'u1', doctor: 'u3', admin: 'u4' },
  users: [],
  mothers: [],
  pregnancies: [],
  visits: [],
  sms: [],
  villages: [],
  rules: []
};

// Four ANC contacts as per the national schedule (weeks from LMP)
const ANC_WEEKS = [12, 20, 28, 36];

/* ---------- lookups ---------- */
const userById = id => S.users.find(u => u.id === id);
const motherOf = p => S.mothers.find(m => m.id === p.motherId);
const visitsOf = p => S.visits.filter(v => v.pregnancyId === p.id).sort((a, b) => a.no - b.no);
const activePregnancies = () => S.pregnancies.filter(p => p.status === 'active');
const gestationalWeek = (p, at = TODAY) => Math.floor((at - p.lmp) / DAY / 7);
const nextVisit = p => visitsOf(p).find(v => !v.actualDate);
const firstName = name => {
  const n = typeof name === 'object' ? name : { en: name, gu: name };
  return { en: n.en.split(' ')[0], gu: (n.gu || n.en).split(' ')[0] };
};

/* ---------- ANCVisit ---------- */
// Status of a visit: done / missed / due (within 7 days) / upcoming
function visitStatus(v) {
  if (v.actualDate) return 'done';
  if (v.scheduledDate < TODAY) return 'missed';
  if ((v.scheduledDate - TODAY) / DAY <= 7) return 'due';
  return 'upcoming';
}

// ANCVisit.checkRisk(): returns the rules a set of readings trips
function checkRisk(readings, mother) {
  const passes = (r, x) => {
    if (x == null || x === '' || isNaN(x)) return false;
    if (r.op === '>=') return x >= r.value;
    if (r.op === '>') return x > r.value;
    return x < r.value;
  };
  const hits = S.rules.filter(r => passes(r, +(r.param === 'age' ? mother.age : readings?.[r.param])));
  // a stricter rule on the same reading hides the milder one (Hb < 7 over Hb < 10)
  return hits.filter(h => !(h.sev === 'moderate' && hits.some(o => o !== h && o.param === h.param && o.sev === 'high')));
}

// Overall risk of a pregnancy, from the latest completed visit plus the mother's age
function assess(p) {
  const done = visitsOf(p).filter(v => v.actualDate);
  const last = done[done.length - 1];
  const hits = checkRisk(last, motherOf(p));
  const level = hits.some(h => h.sev === 'high') ? 'high' : hits.length ? 'moderate' : 'normal';
  return { level, hits, reasons: [...new Set(hits.map(h => h.reason))], last };
}

/* ---------- Pregnancy ---------- */
// Pregnancy.generateSchedule(): first visit is never in the past; later visits keep a 2-week gap
function generateSchedule(p) {
  const dates = [];
  for (const w of ANC_WEEKS) {
    let d = addDays(p.lmp, w * 7);
    if (!dates.length) { dates.push(d < TODAY ? TODAY : d); continue; }
    if (d > addDays(dates[dates.length - 1], 14) && d < p.edd) dates.push(d);
  }
  return dates.map((d, i) => ({ id: newId('v'), pregnancyId: p.id, no: i + 1, scheduledDate: d, actualDate: null }));
}

/* ---------- NotificationService ---------- */
// "to" is a phone number (mother) or a user id (staff). Text is stored as a key + values
// so the log can be shown in either language.
function sendSms(to, kind, msg, vars = {}, alert = false) {
  S.sms.unshift({ at: new Date(), to, kind, msg, vars, alert });
}

function dateFromApi(value) {
  if (!value) return null;
  const datePart = value.slice(0, 10);
  return new Date(`${datePart}T00:00:00`);
}

async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_ROOT}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...options.headers }
  });
  // Some successful endpoints have no body; parse JSON only when a response is present.
  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (!response.ok) {
    let message = body?.detail;
    if (Array.isArray(message)) message = message.map(item => item.msg).join('; ');
    if (message && typeof message === 'object') message = message.message || JSON.stringify(message);
    throw new Error(message || `API request failed (${response.status})`);
  }
  return body;
}

async function loadData() {
  // Load independent resources together, then normalize API field names for existing UI code.
  const [users, pregnancies, sms, rules, villages] = await Promise.all([
    apiRequest('/users'), apiRequest('/pregnancies'), apiRequest('/sms'), apiRequest('/risk-rules'),
    apiRequest('/villages')
  ]);
  S.users = users;
  S.villages = villages;
  // The API uses snake_case and nested records; the UI uses camelCase lookup relationships.
  S.pregnancies = pregnancies.map(p => ({
    id: p.id, motherId: p.mother.id, lmp: dateFromApi(p.lmp), edd: dateFromApi(p.edd),
    gravida: p.gravida, parity: p.parity, status: p.status, reviewed: p.reviewed,
    notes: p.reviews.map(note => ({
      at: dateFromApi(note.created_at), by: note.by_id, decision: note.decision, text: note.text
    }))
  }));
  S.mothers = pregnancies.map(p => ({
    id: p.mother.id, name: p.mother.name, age: p.mother.age, phone: p.mother.phone,
    village: p.mother.village, bloodGroup: p.mother.blood_group, ashaId: p.mother.asha_id
  }));
  S.visits = pregnancies.flatMap(p => p.visits.map(visit => ({
    id: visit.id, pregnancyId: visit.pregnancy_id, no: visit.no,
    scheduledDate: dateFromApi(visit.scheduled_date), actualDate: dateFromApi(visit.actual_date),
    weight: visit.weight, bpSys: visit.bp_sys, bpDia: visit.bp_dia,
    hb: visit.hb, notes: visit.notes
  })));
  S.sms = sms.map(message => ({
    at: new Date(message.created_at), to: message.recipient, kind: message.kind,
    msg: message.message_key, vars: message.variables, alert: message.alert
  }));
  S.rules = rules.map(rule => ({
    ...rule, param: ({ bp_sys: 'bpSys', bp_dia: 'bpDia' })[rule.param] || rule.param
  }));
}

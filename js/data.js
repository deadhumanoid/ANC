// Sample data and domain logic.
// Records mirror the Lab 3 classes: User, Mother, Pregnancy, ANCVisit, NotificationService.
// Everything lives in memory; the backend will replace this file later.

const DAY = 86400000;
const startOfDay = d => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
const addDays = (d, n) => new Date(d.getTime() + n * DAY);
const TODAY = startOfDay(new Date());

let idCounter = 100;
const newId = prefix => prefix + (++idCounter);

const S = {
  role: 'asha',
  me: { asha: 'u1', doctor: 'u3', admin: 'u4' },
  users: [
    { id: 'u1', role: 'asha', name: { en: 'Sunita Parmar', gu: 'સુનિતા પરમાર' }, village: 'bakrol' },
    { id: 'u2', role: 'asha', name: { en: 'Jayshree Macwan', gu: 'જયશ્રી મેકવાન' }, village: 'gana' },
    { id: 'u3', role: 'doctor', name: { en: 'Dr. Nirav Mehta', gu: 'ડૉ. નિરવ મહેતા' } },
    { id: 'u4', role: 'admin', name: { en: 'Kalpana Desai', gu: 'કલ્પના દેસાઈ' } }
  ],
  mothers: [],
  pregnancies: [],
  visits: [],
  sms: [],
  // RiskRule: configurable thresholds, not hard-coded if statements
  rules: [
    { id: 'r1', param: 'bpSys', op: '>=', value: 140, unit: 'u_mmHg', sev: 'high', reason: 'r_highbp' },
    { id: 'r2', param: 'bpDia', op: '>=', value: 90, unit: 'u_mmHg', sev: 'high', reason: 'r_highbp' },
    { id: 'r3', param: 'hb', op: '<', value: 7, unit: 'u_gdl', sev: 'high', reason: 'r_sevan' },
    { id: 'r4', param: 'hb', op: '<', value: 10, unit: 'u_gdl', sev: 'moderate', reason: 'r_an' },
    { id: 'r5', param: 'age', op: '<', value: 18, unit: 'u_yrs', sev: 'moderate', reason: 'r_teen' },
    { id: 'r6', param: 'age', op: '>', value: 35, unit: 'u_yrs', sev: 'moderate', reason: 'r_old' }
  ]
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

/* ---------- sample data ---------- */
function seed(mother, lmpDaysAgo, readings, extra = {}) {
  const m = { id: newId('m'), bloodGroup: 'B+', ...mother };
  S.mothers.push(m);
  const lmp = addDays(TODAY, -lmpDaysAgo);
  const p = {
    id: newId('p'), motherId: m.id, lmp, edd: addDays(lmp, 280),
    gravida: extra.g || 1, parity: extra.pa || 0, status: 'active',
    reviewed: !!extra.reviewed, notes: extra.notes || []
  };
  S.pregnancies.push(p);
  ANC_WEEKS.forEach((w, i) => {
    const scheduled = addDays(lmp, w * 7);
    const r = readings[i];
    S.visits.push({
      id: newId('v'), pregnancyId: p.id, no: i + 1, scheduledDate: scheduled,
      actualDate: r ? addDays(scheduled, r.late || 0) : null,
      weight: r?.weight, bpSys: r?.bp?.[0], bpDia: r?.bp?.[1], hb: r?.hb, notes: r?.notes || ''
    });
  });
  return p;
}

const kavita = seed({ name: { en: 'Kavita Solanki', gu: 'કવિતા સોલંકી' }, age: 24, phone: '9824513306', village: 'bakrol', ashaId: 'u1', bloodGroup: 'O+' }, 212, [
  { weight: 51, bp: [112, 72], hb: 11.2 },
  { weight: 55, bp: [118, 78], hb: 10.8 },
  { weight: 59, bp: [146, 94], hb: 10.9, late: 1, notes: { en: 'Mild swelling in feet', gu: 'પગમાં હળવો સોજો' } }
]);
seed({ name: { en: 'Rekha Vaghela', gu: 'રેખા વાઘેલા' }, age: 19, phone: '9726600418', village: 'bakrol', ashaId: 'u1' }, 146, [
  { weight: 46, bp: [108, 70], hb: 9.2, notes: { en: 'IFA tablets given', gu: 'IFA ગોળીઓ આપી' } }
]);
seed({ name: { en: 'Hina Chauhan', gu: 'હિના ચૌહાણ' }, age: 28, phone: '9909134562', village: 'vadod', ashaId: 'u1', bloodGroup: 'A+' }, 98, [
  { weight: 58, bp: [116, 74], hb: 11.6 }
], { g: 2, pa: 1 });
seed({ name: { en: 'Meena Parmar', gu: 'મીના પરમાર' }, age: 37, phone: '9638221790', village: 'bakrol', ashaId: 'u1', bloodGroup: 'AB+' }, 244, [
  { weight: 60, bp: [120, 80], hb: 9.6 },
  { weight: 63, bp: [122, 80], hb: 8.1 },
  { weight: 65, bp: [124, 82], hb: 6.8, notes: { en: 'Complains of tiredness', gu: 'થાકની ફરિયાદ' } }
], {
  g: 3, pa: 2, reviewed: true,
  notes: [{
    at: addDays(TODAY, -20), by: 'u3', decision: 'dRefer',
    text: { en: 'Severe anaemia at 32 weeks. Referred to CHC Anand for IV iron and a blood test.', gu: '32 અઠવાડિયે ગંભીર એનિમિયા. IV આયર્ન અને લોહીની તપાસ માટે CHC આણંદ રિફર કર્યા.' }
  }]
});
const sonal = seed({ name: { en: 'Sonal Padhiyar', gu: 'સોનલ પઢિયાર' }, age: 26, phone: '9879045521', village: 'vadod', ashaId: 'u1' }, 250, [
  { weight: 54, bp: [110, 70], hb: 11 },
  { weight: 57, bp: [114, 72], hb: 11.3 },
  { weight: 61, bp: [116, 76], hb: 11.1 }
], { g: 2, pa: 1 });
seed({ name: { en: 'Pooja Rathod', gu: 'પૂજા રાઠોડ' }, age: 21, phone: '9913370864', village: 'gana', ashaId: 'u2' }, 186, [
  { weight: 49, bp: [110, 70], hb: 10.4 },
  { weight: 53, bp: [112, 74], hb: 10.6 }
]);
seed({ name: { en: 'Nisha Makwana', gu: 'નિશા મકવાણા' }, age: 30, phone: '9724482017', village: 'gana', ashaId: 'u2', bloodGroup: 'B-' }, 70, []);
seed({ name: { en: 'Bhavna Rohit', gu: 'ભાવના રોહિત' }, age: 17, phone: '9601157732', village: 'gana', ashaId: 'u2' }, 160, [
  { weight: 44, bp: [104, 66], hb: 10.2 }
]);

// keep one visit due this week so the demo always has something to record
visitsOf(sonal)[3].scheduledDate = addDays(TODAY, 2);

// a little message history
sendSms('9824513306', 'k_reminder', 'm_reminder', { name: firstName(motherOf(kavita).name), date: visitsOf(kavita)[2].scheduledDate, village: { k: 'v_bakrol' } });
S.sms[0].at = addDays(new Date(), -3);
sendSms('u3', 'k_alert', 'm_alert', { name: motherOf(kavita).name, village: { k: 'v_bakrol' }, w: gestationalWeek(kavita), reasons: ['r_highbp'] }, true);
S.sms[0].at = addDays(new Date(), -1);

// UI strings in English and Gujarati.
// t(key, vars) looks up the current language; {placeholders} are filled from vars.

const STRINGS = {
  en: {
    appName: 'Maternal Care Coordinator',
    phcName: 'PHC Bakrol',
    navAsha: 'ASHA worker', navDoctor: 'Doctor', navAdmin: 'PHC admin', navSms: 'SMS log',
    protoNote: 'Connected to the local API. Seeded DEMO records are fictional; SMS is simulated and never sent to phones.',
    backendConnecting: 'Connecting to local API…', backendOfflineTitle: 'Backend unavailable',
    backendOffline: 'Could not reach {url}. Start the FastAPI server and retry.', backendRetry: 'Retry connection',

    v_bakrol: 'Bakrol', v_vadod: 'Vadod', v_gana: 'Gana',
    v_vallabh_vidyanagar: 'Vallabh Vidyanagar', v_umreth: 'Umreth', v_petlad: 'Petlad',

    // statuses
    s_done: 'Completed', s_missed: 'Missed', s_due: 'Due this week', s_upcoming: 'Upcoming',
    s_high: 'High risk', s_moderate: 'Moderate risk', s_normal: 'Normal',

    // common
    anc: 'ANC {n}', weeksN: '{n} weeks', yrs: '{n} yrs', open: 'Open', back: '← Back',
    record: 'Record', cancel: 'Cancel', allDone: 'All done', unknown: 'Unknown',
    colName: 'Name', colVisit: 'Visit', colScheduled: 'Scheduled', colStatus: 'Status',
    colWeek: 'Week', colEdd: 'Due date', colNext: 'Next visit', colRisk: 'Risk',
    colReadings: 'Readings', colDecision: 'Decision', colNote: 'Note', colDate: 'Date',
    colReasons: 'Reasons', colVillage: 'Village',
    reads: 'BP {bp} · Hb {hb} g/dL · {wt} kg',

    // ASHA home
    hello: 'Namaste, {name}',
    statMothers: 'mothers', statDue: 'due this week', statMissed: 'missed visits', statHigh: 'high risk',
    btnRegister: 'Register pregnant woman',
    hNeeds: 'Needs a visit', subNeeds: 'Missed checkups and those due this week',
    noneNeeds: 'Nothing missed or due this week.',
    hMyMothers: 'My mothers',

    // ANC card
    fPhone: 'Phone', fBlood: 'Blood group', fGP: 'Gravida / Para', fLmp: 'Last period (LMP)',
    fEdd: 'Expected delivery (EDD)', fWeek: 'Current week', fAsha: 'ASHA worker',
    riskLabel: 'Risk:',
    hVisits: 'ANC visits', hNotes: "Doctor's notes",
    hRecord: 'Record ANC {n}', recSub: 'Visit date: today, {date} · {w} weeks',
    lSys: 'Systolic BP (mmHg)', lDia: 'Diastolic BP (mmHg)', lHb: 'Haemoglobin (g/dL)',
    lWt: 'Weight (kg)', lNotes: 'Notes', phNotes: 'Symptoms, tablets given, advice',
    saveVisit: 'Save visit and check risk',
    resHigh: 'Visit saved. Risk check: high risk. {doc} has been alerted and the case is in the doctor’s queue.',
    resModerate: 'Visit saved. Risk check: moderate risk. The case is on the doctor’s watch list.',
    resNormal: 'Visit saved. Risk check: normal. No rule was triggered.',

    // register
    regSub: 'Creates her record, calculates the due date and schedules ANC visits.',
    gName: 'Full name', gAge: 'Age', gPhone: 'Mobile number', gVillage: 'Village',
    gGrav: 'Gravida', gPara: 'Para',
    regHint: 'Duplicate checks use active records already stored in the local database.',
    regSubmit: 'Register and schedule visits',
    errDup: '{name} is already registered with {phone} and has an active pregnancy. Open her record instead of registering again.',
    errLmp: 'That date is more than 40 weeks ago. Check the LMP.',
    toastReg: 'Registered {name}. {n} ANC visits scheduled.',

    // doctor
    docNote: 'Flags come from threshold rules set by the PHC. They point you to cases to look at and are not a diagnosis.',
    statQueue: 'awaiting review', statWatch: 'on watch list', statReviewed: 'reviewed', statActive: 'active pregnancies',
    hQueue: 'High-risk queue', subQueue: 'Flagged after the latest visit and not yet reviewed',
    noneQueue: 'No cases waiting. New flags appear here as soon as an ASHA worker records a visit.',
    metaCase: '{village} · {w} weeks · G{g} P{p} · ASHA: {asha}',
    lastVisit: 'last visit {date}',
    phDocNote: 'Note for the record and the ASHA worker',
    dRoutine: 'Continue routine ANC', dPhc: 'Call for PHC visit', dRefer: 'Refer to CHC/FRU',
    saveReview: 'Save review', needNote: 'Add a short note before saving the review.',
    toastReview: 'Review saved for {name}.',
    hWatch: 'Watch list', subWatch: 'Moderate risk, no action needed yet', noneWatch: 'Nobody on the watch list.',
    hReviewed: 'Reviewed', noneReviewed: 'Nothing reviewed yet.',

    // admin
    hAdmin: 'PHC Bakrol coverage', adminSub: '{name}, administrator · {date}',
    statRegistered: 'registered pregnancies', statOnTrack: 'of due visits done',
    hCompletion: 'ANC completion by visit', subCompletion: 'Completed, out of visits whose date has passed',
    hByAsha: 'By ASHA worker',
    colMothers: 'Mothers', colDone: 'Done', colMissed: 'Missed', colOnTrack: 'On track', colHigh: 'High risk',
    hRules: 'Risk rules', subRules: 'Checked after every visit. Change a value and every case is re-checked straight away.',
    colReading: 'Reading', colCondition: 'Condition', colFlag: 'Flag as', colShownAs: 'Shown as',
    toastRule: '{label} rule is now {op} {n} {unit}. All cases re-checked.',
    p_bpSys: 'Systolic BP', p_bpDia: 'Diastolic BP', p_hb: 'Haemoglobin', p_age: 'Mother’s age',
    u_mmHg: 'mmHg', u_gdl: 'g/dL', u_yrs: 'yrs',
    r_highbp: 'High BP', r_sevan: 'Severe anaemia', r_an: 'Anaemia', r_teen: 'Age under 18', r_old: 'Age over 35',

    // sms
    hSms: 'SMS log', subSms: 'Simulated messages recorded by the notification service, newest first. Nothing is sent to phones.',
    runJob: 'Run daily reminder job', noSms: 'No messages yet.',
    colTime: 'Sent', colTo: 'To', colType: 'Type', colMsg: 'Message',
    toastJob: 'Reminders sent: {r}. Missed-visit notices sent: {m}.',
    toastJobNone: 'Nothing to send. Everyone due soon has already been reminded today.',
    k_reminder: 'Reminder', k_alert: 'Alert', k_reg: 'Registration', k_visit: 'Visit recorded',
    k_missed: 'Missed visit', k_referral: 'Referral', k_docvisit: 'Doctor visit', k_docnote: 'Doctor note',

    m_reminder: '{name} ben, your ANC checkup is on {date}. Please come to the Anganwadi centre, {village}.',
    m_alert: '{name} ({village}, {w} weeks) flagged high risk: {reasons}. Please review.',
    m_reg: '{name} ben, you are registered for antenatal care. Expected delivery: {edd}. First checkup: {date}.',
    m_visit: '{name} ben, your checkup is recorded. Next checkup: {date}.',
    m_visitLast: '{name} ben, your checkup is recorded. That was your last scheduled ANC visit.',
    m_missed: '{name} ben, you missed your checkup on {date}. Your ASHA worker will contact you.',
    m_missedAsha: '{name} missed ANC {n} ({date}). Please follow up.',
    m_referral: '{name} ben, the doctor has referred you to CHC Anand. Your ASHA worker will help you get there.',
    m_docvisit: '{name} ben, please come to PHC Bakrol to see the doctor this week.',
    m_docnote: '{name}: {decision}. {note}',

    // landing
    lEyebrow: 'For PHC Bakrol and the villages it serves',
    lTitle: 'Every checkup on time. <em>Every mother</em> looked after.',
    lLede: 'One shared record for antenatal care. ASHA workers register mothers and record checkups, risk is flagged the moment a visit is saved, the PHC doctor reviews, and mothers get SMS reminders in Gujarati.',
    lStart: 'Open the app', lHow: 'See how it works',
    lStatPreg: 'mothers being followed', lStatDone: 'checkups recorded', lStatVillages: 'villages covered', lStatAsha: 'ASHA workers',
    lHowTitle: 'How it works',
    lStep1T: 'Register', lStep1: 'The ASHA worker enters her last period date. The due date and four ANC checkups are worked out for her.',
    lStep2T: 'Check up', lStep2: 'At each visit she records BP, haemoglobin and weight. Risk rules run as soon as the visit is saved.',
    lStep3T: 'Review', lStep3: 'High-risk cases go straight to the PHC doctor, who chooses routine care, a PHC visit or a referral.',
    lStep4T: 'Remind', lStep4: 'Mothers get an SMS before each checkup, and the ASHA worker hears about any missed visit.',
    lRolesTitle: 'Choose where to start',
    lAshaDesc: 'Your mothers, who needs a visit this week, and recording checkups.',
    lDocDesc: 'The high-risk queue, the watch list and your past reviews.',
    lAdminDesc: 'Coverage by visit and by ASHA worker, and the risk thresholds.',
    lSmsDesc: 'Every reminder and alert the system has sent.',
    lJourney: 'The four checkups', lBirth: 'Due date', wkShort: '{n} wk',
    lP1T: 'English and ગુજરાતી', lP1: 'The whole app switches language with one tap, including the SMS text.',
    lP2T: 'Flags, not diagnoses', lP2: 'Rules point the doctor to cases worth a look. The doctor decides what happens next.',
    lP3T: 'No app for mothers', lP3: 'Mothers only need a phone that can receive an SMS.'
  },

  gu: {
    appName: 'માતૃ સંભાળ સંકલન',
    phcName: 'PHC બાકરોલ',
    navAsha: 'આશા કાર્યકર', navDoctor: 'ડૉક્ટર', navAdmin: 'PHC વહીવટકર્તા', navSms: 'SMS લોગ',
    protoNote: 'સ્થાનિક API સાથે જોડાયેલું. DEMO રેકોર્ડ કાલ્પનિક છે; SMS માત્ર સિમ્યુલેશન છે અને ફોન પર મોકલાતાં નથી.',
    backendConnecting: 'સ્થાનિક API સાથે જોડાઈ રહ્યું છે…', backendOfflineTitle: 'બેકએન્ડ ઉપલબ્ધ નથી',
    backendOffline: '{url} સાથે જોડાઈ શક્યું નથી. FastAPI સર્વર શરૂ કરીને ફરી પ્રયાસ કરો.', backendRetry: 'ફરી જોડવાનો પ્રયાસ',

    v_bakrol: 'બાકરોલ', v_vadod: 'વડોદ', v_gana: 'ગાના',
    v_vallabh_vidyanagar: 'વલ્લભ વિદ્યાનગર', v_umreth: 'ઉમરેઠ', v_petlad: 'પેટલાદ',

    s_done: 'પૂર્ણ', s_missed: 'ચૂકી ગયા', s_due: 'આ અઠવાડિયે', s_upcoming: 'આગામી',
    s_high: 'ઉચ્ચ જોખમ', s_moderate: 'મધ્યમ જોખમ', s_normal: 'સામાન્ય',

    anc: 'ANC {n}', weeksN: '{n} અઠવાડિયા', yrs: '{n} વર્ષ', open: 'ખોલો', back: '← પાછા',
    record: 'નોંધો', cancel: 'રદ કરો', allDone: 'બધી પૂર્ણ', unknown: 'ખબર નથી',
    colName: 'નામ', colVisit: 'તપાસ', colScheduled: 'નિર્ધારિત તારીખ', colStatus: 'સ્થિતિ',
    colWeek: 'અઠવાડિયું', colEdd: 'પ્રસૂતિ તારીખ', colNext: 'આગામી તપાસ', colRisk: 'જોખમ',
    colReadings: 'માપ', colDecision: 'નિર્ણય', colNote: 'નોંધ', colDate: 'તારીખ',
    colReasons: 'કારણો', colVillage: 'ગામ',
    reads: 'BP {bp} · Hb {hb} g/dL · {wt} કિલો',

    hello: 'નમસ્તે, {name}',
    statMothers: 'માતાઓ', statDue: 'આ અઠવાડિયે બાકી', statMissed: 'ચૂકેલી તપાસ', statHigh: 'ઉચ્ચ જોખમ',
    btnRegister: 'સગર્ભા મહિલાની નોંધણી કરો',
    hNeeds: 'તપાસ બાકી છે', subNeeds: 'ચૂકેલી તપાસ અને આ અઠવાડિયાની તપાસ',
    noneNeeds: 'આ અઠવાડિયે કોઈ તપાસ બાકી નથી.',
    hMyMothers: 'મારી માતાઓ',

    fPhone: 'ફોન', fBlood: 'બ્લડ ગ્રુપ', fGP: 'ગ્રેવિડા / પેરા', fLmp: 'છેલ્લું માસિક (LMP)',
    fEdd: 'અપેક્ષિત પ્રસૂતિ (EDD)', fWeek: 'હાલનું અઠવાડિયું', fAsha: 'આશા કાર્યકર',
    riskLabel: 'જોખમ:',
    hVisits: 'ANC તપાસ', hNotes: 'ડૉક્ટરની નોંધ',
    hRecord: 'ANC {n} નોંધો', recSub: 'તપાસ તારીખ: આજે, {date} · {w} અઠવાડિયા',
    lSys: 'સિસ્ટોલિક BP (mmHg)', lDia: 'ડાયસ્ટોલિક BP (mmHg)', lHb: 'હિમોગ્લોબિન (g/dL)',
    lWt: 'વજન (કિલો)', lNotes: 'નોંધ', phNotes: 'લક્ષણો, આપેલી ગોળીઓ, સલાહ',
    saveVisit: 'તપાસ સાચવો અને જોખમ તપાસો',
    resHigh: 'તપાસ સચવાઈ. જોખમ: ઉચ્ચ. {doc}ને જાણ કરવામાં આવી છે અને કેસ ડૉક્ટરની યાદીમાં છે.',
    resModerate: 'તપાસ સચવાઈ. જોખમ: મધ્યમ. કેસ ડૉક્ટરની નજર યાદીમાં છે.',
    resNormal: 'તપાસ સચવાઈ. જોખમ: સામાન્ય. કોઈ નિયમ લાગુ પડ્યો નથી.',

    regSub: 'તેમનો રેકોર્ડ બનાવે છે, પ્રસૂતિ તારીખ ગણે છે અને ANC તપાસ નક્કી કરે છે.',
    gName: 'પૂરું નામ', gAge: 'ઉંમર', gPhone: 'મોબાઇલ નંબર', gVillage: 'ગામ',
    gGrav: 'ગ્રેવિડા', gPara: 'પેરા',
    regHint: 'ડુપ્લિકેટ ચકાસણી સ્થાનિક ડેટાબેઝમાં રહેલા ચાલુ રેકોર્ડ પરથી થાય છે.',
    regSubmit: 'નોંધણી કરો અને તપાસ નક્કી કરો',
    errDup: '{name} {phone} નંબરથી પહેલેથી નોંધાયેલા છે અને તેમની સગર્ભાવસ્થા ચાલુ છે. ફરી નોંધણી કરવાને બદલે તેમનો રેકોર્ડ ખોલો.',
    errLmp: 'આ તારીખ 40 અઠવાડિયાથી વધુ જૂની છે. LMP તપાસો.',
    toastReg: '{name}ની નોંધણી થઈ. {n} ANC તપાસ નક્કી થઈ.',

    docNote: 'આ ચેતવણીઓ PHCએ નક્કી કરેલા નિયમો પરથી આવે છે. તે જોવા જેવા કેસ બતાવે છે, નિદાન નથી.',
    statQueue: 'સમીક્ષા બાકી', statWatch: 'નજર યાદીમાં', statReviewed: 'સમીક્ષા થઈ', statActive: 'ચાલુ સગર્ભાવસ્થા',
    hQueue: 'ઉચ્ચ જોખમ યાદી', subQueue: 'છેલ્લી તપાસ પછી ફ્લેગ થયેલા, સમીક્ષા બાકી',
    noneQueue: 'કોઈ કેસ બાકી નથી. આશા કાર્યકર તપાસ નોંધે કે તરત નવા કેસ અહીં દેખાશે.',
    metaCase: '{village} · {w} અઠવાડિયા · G{g} P{p} · આશા: {asha}',
    lastVisit: 'છેલ્લી તપાસ {date}',
    phDocNote: 'રેકોર્ડ અને આશા કાર્યકર માટે નોંધ',
    dRoutine: 'નિયમિત ANC ચાલુ રાખો', dPhc: 'PHC મુલાકાત માટે બોલાવો', dRefer: 'CHC/FRU માં રિફર કરો',
    saveReview: 'સમીક્ષા સાચવો', needNote: 'સમીક્ષા સાચવતા પહેલાં ટૂંકી નોંધ લખો.',
    toastReview: '{name} માટે સમીક્ષા સચવાઈ.',
    hWatch: 'નજર યાદી', subWatch: 'મધ્યમ જોખમ, હાલ કોઈ પગલું જરૂરી નથી', noneWatch: 'નજર યાદીમાં કોઈ નથી.',
    hReviewed: 'સમીક્ષા થયેલા', noneReviewed: 'હજુ કોઈ સમીક્ષા થઈ નથી.',

    hAdmin: 'PHC બાકરોલ કવરેજ', adminSub: '{name}, વહીવટકર્તા · {date}',
    statRegistered: 'નોંધાયેલ સગર્ભાવસ્થા', statOnTrack: 'બાકી તપાસમાંથી પૂર્ણ',
    hCompletion: 'તપાસ પ્રમાણે ANC પૂર્ણતા', subCompletion: 'જેની તારીખ વીતી ગઈ છે તેમાંથી પૂર્ણ થયેલી',
    hByAsha: 'આશા કાર્યકર પ્રમાણે',
    colMothers: 'માતાઓ', colDone: 'પૂર્ણ', colMissed: 'ચૂકેલી', colOnTrack: 'સમયસર', colHigh: 'ઉચ્ચ જોખમ',
    hRules: 'જોખમ નિયમો', subRules: 'દરેક તપાસ પછી ચકાસાય છે. કિંમત બદલો એટલે બધા કેસ તરત ફરી ચકાસાશે.',
    colReading: 'માપ', colCondition: 'શરત', colFlag: 'ફ્લેગ', colShownAs: 'કારણ',
    toastRule: '{label} નિયમ હવે {op} {n} {unit}. બધા કેસ ફરી ચકાસ્યા.',
    p_bpSys: 'સિસ્ટોલિક BP', p_bpDia: 'ડાયસ્ટોલિક BP', p_hb: 'હિમોગ્લોબિન', p_age: 'માતાની ઉંમર',
    u_mmHg: 'mmHg', u_gdl: 'g/dL', u_yrs: 'વર્ષ',
    r_highbp: 'હાઈ BP', r_sevan: 'ગંભીર એનિમિયા', r_an: 'એનિમિયા', r_teen: '18 વર્ષથી ઓછી ઉંમર', r_old: '35 વર્ષથી વધુ ઉંમર',

    hSms: 'SMS લોગ', subSms: 'નોટિફિકેશન સર્વિસના સિમ્યુલેટેડ સંદેશા, નવા પહેલા. ફોન પર કંઈ મોકલાતું નથી.',
    runJob: 'દૈનિક રિમાઇન્ડર ચલાવો', noSms: 'હજુ કોઈ સંદેશ નથી.',
    colTime: 'મોકલ્યો', colTo: 'કોને', colType: 'પ્રકાર', colMsg: 'સંદેશ',
    toastJob: 'મોકલેલા રિમાઇન્ડર: {r}. ચૂકેલી તપાસની સૂચના: {m}.',
    toastJobNone: 'મોકલવા જેવું કંઈ નથી. જેમની તપાસ નજીક છે તેમને આજે યાદ અપાવી દીધું છે.',
    k_reminder: 'રિમાઇન્ડર', k_alert: 'ચેતવણી', k_reg: 'નોંધણી', k_visit: 'તપાસ નોંધાઈ',
    k_missed: 'ચૂકેલી તપાસ', k_referral: 'રિફરલ', k_docvisit: 'ડૉક્ટર મુલાકાત', k_docnote: 'ડૉક્ટરની નોંધ',

    m_reminder: '{name} બેન, તમારી ANC તપાસ {date}ના રોજ છે. કૃપા કરીને {village}ના આંગણવાડી કેન્દ્રે આવજો.',
    m_alert: '{name} ({village}, {w} અઠવાડિયા) ઉચ્ચ જોખમમાં ફ્લેગ થયા છે: {reasons}. કૃપા કરી સમીક્ષા કરો.',
    m_reg: '{name} બેન, પ્રસૂતિ પૂર્વ સંભાળ માટે તમારી નોંધણી થઈ છે. અપેક્ષિત પ્રસૂતિ: {edd}. પહેલી તપાસ: {date}.',
    m_visit: '{name} બેન, તમારી તપાસ નોંધાઈ છે. આગામી તપાસ: {date}.',
    m_visitLast: '{name} બેન, તમારી તપાસ નોંધાઈ છે. આ તમારી છેલ્લી નિર્ધારિત ANC તપાસ હતી.',
    m_missed: '{name} બેન, {date}ની તમારી તપાસ ચૂકી ગઈ છે. તમારા આશા કાર્યકર તમારો સંપર્ક કરશે.',
    m_missedAsha: '{name} ANC {n} ({date}) ચૂકી ગયા છે. કૃપા કરી ફોલો-અપ કરો.',
    m_referral: '{name} બેન, ડૉક્ટરે તમને CHC આણંદ રિફર કર્યા છે. તમારા આશા કાર્યકર તમને ત્યાં પહોંચવામાં મદદ કરશે.',
    m_docvisit: '{name} બેન, કૃપા કરી આ અઠવાડિયે ડૉક્ટરને મળવા PHC બાકરોલ આવજો.',
    m_docnote: '{name}: {decision}. {note}',

    lEyebrow: 'PHC બાકરોલ અને તેના ગામો માટે',
    lTitle: 'દરેક તપાસ સમયસર. <em>દરેક માતા</em>ની સંભાળ.',
    lLede: 'પ્રસૂતિ પૂર્વ સંભાળ માટે એક જ સહિયારો રેકોર્ડ. આશા કાર્યકર માતાની નોંધણી કરે અને તપાસ નોંધે, તપાસ સચવાતાં જ જોખમ ચકાસાય, PHC ડૉક્ટર સમીક્ષા કરે, અને માતાઓને ગુજરાતીમાં SMS યાદી મળે.',
    lStart: 'એપ ખોલો', lHow: 'કેવી રીતે કામ કરે છે',
    lStatPreg: 'માતાઓની સંભાળ ચાલુ', lStatDone: 'તપાસ નોંધાઈ', lStatVillages: 'ગામો', lStatAsha: 'આશા કાર્યકરો',
    lHowTitle: 'કેવી રીતે કામ કરે છે',
    lStep1T: 'નોંધણી', lStep1: 'આશા કાર્યકર છેલ્લા માસિકની તારીખ લખે. પ્રસૂતિ તારીખ અને ચાર ANC તપાસ આપોઆપ નક્કી થાય.',
    lStep2T: 'તપાસ', lStep2: 'દરેક મુલાકાતે BP, હિમોગ્લોબિન અને વજન નોંધાય. તપાસ સચવાતાં જ જોખમ નિયમો ચકાસાય.',
    lStep3T: 'સમીક્ષા', lStep3: 'ઉચ્ચ જોખમવાળા કેસ સીધા PHC ડૉક્ટર પાસે જાય, જે નિયમિત સંભાળ, PHC મુલાકાત કે રિફરલ નક્કી કરે.',
    lStep4T: 'યાદી', lStep4: 'દરેક તપાસ પહેલાં માતાને SMS મળે, અને તપાસ ચૂકાય તો આશા કાર્યકરને જાણ થાય.',
    lRolesTitle: 'ક્યાંથી શરૂ કરવું છે?',
    lAshaDesc: 'તમારી માતાઓ, આ અઠવાડિયે કોની તપાસ બાકી છે, અને તપાસ નોંધવી.',
    lDocDesc: 'ઉચ્ચ જોખમ યાદી, નજર યાદી અને તમારી અગાઉની સમીક્ષાઓ.',
    lAdminDesc: 'તપાસ અને આશા કાર્યકર પ્રમાણે કવરેજ, અને જોખમ મર્યાદાઓ.',
    lSmsDesc: 'સિસ્ટમે મોકલેલી દરેક યાદી અને ચેતવણી.',
    lJourney: 'ચાર તપાસ', lBirth: 'પ્રસૂતિ તારીખ', wkShort: '{n} અઠ.',
    lP1T: 'English અને ગુજરાતી', lP1: 'એક ક્લિકમાં આખી એપની ભાષા બદલાય, SMS સહિત.',
    lP2T: 'ચેતવણી, નિદાન નહીં', lP2: 'નિયમો ડૉક્ટરને જોવા જેવા કેસ બતાવે છે. આગળ શું કરવું તે ડૉક્ટર નક્કી કરે.',
    lP3T: 'માતાઓ માટે એપ નહીં', lP3: 'માતાઓને ફક્ત SMS આવી શકે એવો ફોન જોઈએ.'
  }
};

let LANG = 'en';
try { LANG = localStorage.getItem('mcc-lang') === 'gu' ? 'gu' : 'en'; } catch (e) { /* storage unavailable */ }

function setLang(lang) {
  LANG = lang;
  try { localStorage.setItem('mcc-lang', lang); } catch (e) { /* ignore */ }
}

function esc(s) {
  return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// Values stored in both languages look like { en: '...', gu: '...' }.
function L(x) {
  return x && typeof x === 'object' && !(x instanceof Date) ? (x[LANG] || x.en) : x;
}

const locale = () => (LANG === 'gu' ? 'gu-IN' : 'en-IN');
const fmt = d => (d ? d.toLocaleDateString(locale(), { day: 'numeric', month: 'short', year: 'numeric' }) : '—');
const fmtShort = d => (d ? d.toLocaleDateString(locale(), { day: 'numeric', month: 'short' }) : '—');

// Placeholder values can be: a Date, a list of string keys, { k: key }, a bilingual object, or plain text.
// Output is HTML-escaped, so it is safe to put into innerHTML.
function t(key, vars = {}) {
  const s = STRINGS[LANG][key] ?? STRINGS.en[key] ?? key;
  return esc(s).replace(/\{(\w+)\}/g, (_, name) => {
    const v = vars[name];
    if (v == null) return '';
    if (v instanceof Date) return esc(fmt(v));
    if (Array.isArray(v)) return v.map(k => t(k)).join(', ');
    if (typeof v === 'object' && v.k) return t(v.k);
    return esc(L(v));
  });
}

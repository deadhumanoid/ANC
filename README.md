# Maternal Care Coordinator

A clickable front-end prototype of a maternal (antenatal) care coordination system for primary health centres in India. It is built for the three people who run antenatal care in a village: the **ASHA worker** who registers pregnant women and records checkups, the **doctor** at the PHC who reviews high-risk cases, and the **PHC administrator** who tracks coverage. Mothers do not log in; they receive SMS reminders.

This is the Software Engineering Lab semester project. This version is the prototype for Labs 1–5 (requirements, class design, interaction design and architecture). There is no backend yet: all data is sample data held in memory and resets when the page reloads.

The whole interface can be switched between **English and Gujarati** with one click.

## Running it

No build step and no dependencies. Either:

- open `index.html` in a browser, or
- enable GitHub Pages for the repository (Settings → Pages → deploy from the `main` branch, root folder) and open the published link.

## What you can do

| Role | Features |
|---|---|
| ASHA worker | See missed and due visits; register a pregnant woman (EDD is calculated and four ANC visits are scheduled); record a visit with BP, haemoglobin and weight; see each mother's ANC card |
| Doctor | Review the high-risk queue, add a note and a decision (routine ANC, call to PHC, refer to CHC/FRU); see the moderate-risk watch list and past reviews |
| PHC admin | ANC coverage by visit and by ASHA worker; edit the risk-rule thresholds |
| SMS log | Every message the notification service sent; run the daily reminder job |

Things worth trying:

- Register with phone number `9824513306` to see the duplicate check.
- Record a visit with systolic BP ≥ 140 or Hb < 7. The case is flagged high risk and appears in the doctor's queue, and an alert shows up in the SMS log.
- In the admin view, change the anaemia threshold from 10 to 11. Every case is re-checked immediately, because risk rules are data, not code.

## How it maps to the lab documents

| Lab | In the prototype |
|---|---|
| Labs 1–2 (SRS, use cases) | Three logged-in actors plus the mother as an SMS-only stakeholder; registration, scheduling, reminders, visit recording, risk flagging, doctor review, coverage reports |
| Lab 3 (class design) | `js/data.js` keeps `Mother`, `Pregnancy` and `ANCVisit` as separate records. `generateSchedule()`, `visitStatus()` (missed check), `checkRisk()` and `sendSms()` correspond to the class methods |
| Lab 4 (interaction design) | *Register pregnant woman* (with the duplicate-phone alternative flow) and *Record ANC visit with high-risk detection* follow the two sequence diagrams |
| Lab 5 (architecture) | Web client only. Offline sync (NFR3) is deferred to a later iteration, as noted in the SRS |

Risk rules used by default (editable in the admin view): systolic BP ≥ 140, diastolic BP ≥ 90, Hb < 7 → high risk; Hb < 10, age < 18, age > 35 → moderate risk. These are illustrative thresholds for the prototype, not clinical guidance, and the system flags cases for a doctor to review rather than diagnosing.

## Project structure

```
index.html        page shell: header, navigation, language button
css/style.css     all styles (light and dark)
js/i18n.js        English and Gujarati strings, t() lookup, date formatting
js/data.js        sample data and domain logic (schedule, risk check, notifications)
js/app.js         screens for each role and event handling
```

To add a string, add the same key to both `en` and `gu` in `js/i18n.js` and use `t('key')` in `app.js`.

## Next steps

- REST API and MySQL database behind the same screens (three-tier architecture from Lab 5)
- Real login with role-based access
- SMS gateway integration for reminders and alerts
- Offline data entry and sync for ASHA workers (NFR3)

## Team

- Sruja Brahmbhatt — Product Owner, developer
- Priyanshi Shah — Scrum Master, developer

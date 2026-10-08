# Maternal Care Coordinator

A clickable front-end prototype of a maternal (antenatal) care coordination system for primary health centres in India. It is built for the three people who run antenatal care in a village: the **ASHA worker** who registers pregnant women and records checkups, the **doctor** at the PHC who reviews high-risk cases, and the **PHC administrator** who tracks coverage. Mothers do not log in; they receive SMS reminders.

This is the Software Engineering Lab semester project. This version is the prototype for Labs 1–5 (requirements, class design, interaction design and architecture). There is no backend yet: all data is sample data held in memory and resets when the page reloads.

The whole interface can be switched between **English and Gujarati** with one click.

## Running it

Either:
- open `index.html` in a browser, or
- enable GitHub Pages for the repository (Settings → Pages → deploy from the `main` branch, root folder) and open the published link.

## FastAPI backend

The backend lives in `backend/` and provides a REST API for pregnancies, ANC visits, risk rules, PHC coverage, doctor reviews, and the simulated SMS log. The static frontend above remains the original in-memory prototype and is not connected to the API yet.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py -m uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API. The default SQLite database is created at `backend/anc.db`; copy `.env.example` to `.env` and set `DATABASE_URL` to use MySQL (`mysql+pymysql://...`). The API seeds staff accounts and editable risk thresholds on first startup, but does not seed any mother/pregnancy records. Run tests with `py -m pytest`.

This is a development backend, not a production clinical system: authentication and role-based authorization are not implemented, and SMS delivery is simulated. Risk thresholds are illustrative and are not clinical guidance.

## What each user can do

| Role | Features |
|---|---|
| ASHA worker | See missed and due visits; register a pregnant woman (EDD is calculated and four ANC visits are scheduled); record a visit with BP, haemoglobin and weight; see each mother's ANC card |
| Doctor | Review the high-risk queue, add a note and a decision (routine ANC, call to PHC, refer to CHC/FRU); see the moderate-risk watch list and past reviews |
| PHC admin | ANC coverage by visit and by ASHA worker; edit the risk-rule thresholds |
| SMS log | Every message the notification service sent; run the daily reminder job |


## Risk rules

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

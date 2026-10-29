# Maternal Care Coordinator

A clickable front-end prototype of a maternal (antenatal) care coordination system for primary health centres in India. It is built for the three people who run antenatal care in a village: the **ASHA worker** who registers pregnant women and records checkups, the **doctor** at the PHC who reviews high-risk cases, and the **PHC administrator** who tracks coverage. Mothers do not log in; they receive SMS reminders.

This is the Software Engineering Lab semester project. The frontend keeps the prototype's role-based screens and connects to a local FastAPI backend for persistent records.

The whole interface can be switched between **English and Gujarati** with one click.

The app opens on a **landing page** that explains the workflow (register → check up → review → remind), shows live counts from the database, and lets you pick a role to start from. Click the logo in the header to return to it.

## Running locally

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

**Windows (PowerShell)**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn backend.main:app --reload
```

Open `http://127.0.0.1:8000/` to use the app and `http://127.0.0.1:8000/docs` for interactive API docs. FastAPI serves the frontend and API from the same origin; no second static server or CORS configuration is needed for local use.

The backend lives in `backend/` and provides REST endpoints for pregnancies, ANC visits, supported villages, risk rules, PHC coverage, doctor reviews, and the simulated SMS log. SQLite is created at `backend/anc.db`; the API seeds staff, risk thresholds, and village names on first startup. On an empty database it also adds three clearly labeled fictional DEMO pregnancy records with synthetic measurements; existing mother records are left untouched. The registration form uses the supported-village list. The SMS page's reminder button runs the notification job, stores simulated messages in the database, and is safe to run repeatedly on the same day. No messages are sent to phones. The UI role tabs are demonstration-only, not authentication. See [Testing](#testing) for the automated tests.

To use MySQL, set `DATABASE_URL` in the environment before starting Uvicorn, for example `mysql+pymysql://anc_user:password@localhost:3306/anc`. Create the database first. `.env.example` documents the supported settings; `.env` files are not loaded automatically.

This is a development backend, not a production clinical system: authentication and role-based authorization are not implemented, and SMS delivery is simulated. Risk thresholds are illustrative and are not clinical guidance.

## What each user can do

| Role | Features |
|---|---|
| Landing page | What the system does, live counts, how it works, and a card for each role |
| ASHA worker | See missed and due visits; register a pregnant woman (EDD is calculated and four ANC visits are scheduled); record a visit with BP, haemoglobin and weight; see each mother's ANC card |
| Doctor | Review the high-risk queue, add a note and a decision (routine ANC, call to PHC, refer to CHC/FRU); see the moderate-risk watch list and past reviews |
| PHC admin | ANC coverage by visit and by ASHA worker; edit the risk-rule thresholds |
| SMS log | Every message the notification service sent; run the daily reminder job |


## Risk rules

Risk rules used by default (editable in the admin view): systolic BP ≥ 140, diastolic BP ≥ 90, Hb < 7 → high risk; Hb < 10, age < 18, age > 35 → moderate risk. These are illustrative thresholds for the prototype, not clinical guidance, and the system flags cases for a doctor to review rather than diagnosing.

## Project structure

```
index.html        page shell: header, navigation, language button
css/style.css     all styles: warm light and dark themes, landing page
js/i18n.js        English and Gujarati strings, t() lookup, date formatting
js/data.js        API client and frontend data adapter
js/app.js         landing page, screens for each role and event handling
backend/          FastAPI app, database models, domain logic, request schemas
tests/unit/       unit tests: scheduling, visit status, risk rules, input validation
tests/integration/ integration tests: full API requests through the database
pytest.ini        test settings (test folder, import path, unit/integration markers)
```

To add a string, add the same key to both `en` and `gu` in `js/i18n.js` and use `t('key')` in `app.js`.

## Testing

The backend has two layers of automated tests, written with **pytest**.

- **Unit tests** (`tests/unit/`) call one function or schema directly with fixed inputs and a fixed date, so their results never depend on the day they run. They check the rules on their own, without a server.
- **Integration tests** (`tests/integration/`) send real HTTP requests through FastAPI with a test client. Each request goes through validation, domain logic and the database, then back as a response. They check that the pieces work together.

Every test starts from a fresh **in-memory SQLite database**, seeded with the default staff, risk rules, villages and the three DEMO mothers (`tests/conftest.py`). Tests never touch `backend/anc.db` and never affect each other. Integration-test dates are calculated from today, so the suite keeps passing over time.

### Running the tests

```bash
source .venv/bin/activate                       # Windows: .venv\Scripts\Activate.ps1
python -m pytest -v                             # everything, one line per test
python -m pytest -m unit -v                     # only unit tests
python -m pytest -m integration -v              # only integration tests
python -m pytest -v -k "schedule or risk"       # tests whose names match
```

### What is tested

**Unit tests**

| File | Function | Edge cases covered |
|---|---|---|
| `test_visit_status.py` | `visit_status()` | Missed if the date has passed (yesterday is the last missed day); due from today up to exactly 7 days ahead; upcoming from 8 days; a recorded visit is always done, even if late or early |
| `test_schedule.py` | `generate_schedule()` | Early registration gets visits at weeks 12/20/28/36; registration on the LMP day; exactly at week 12; late registration moves the first visit to today; a visit exactly 14 days after the previous one is dropped, 15 days is kept; very late registration (week 35, 39) gets one visit today; no later visit on or after the due date; plus a sweep of **every week from 0 to 39** checking the four scheduling rules each time |
| `test_risk.py` | `risk_hits()`, `pregnancy_assessment()` | Each threshold just below and at its limit (systolic 139/140, diastolic 89/90, Hb 10.0/9.9/7.0/6.9, age 17/18/35/36); severe anaemia hides plain anaemia; several problems at once; no visit yet means only age is checked; an edited threshold applies immediately; high beats moderate; reasons are not repeated; only the latest recorded visit counts, by visit number rather than list order; unrecorded visits are ignored |
| `test_schemas.py` | Request schemas | Valid and invalid mobile numbers (wrong first digit, 9/11 digits, letters, +91); age 12/55 accepted, 11/56 rejected; readings accepted at their exact limits and rejected one step outside; fractional BP rejected; every reading required; only the three doctor decisions accepted; empty or overlong notes rejected; rule values limited to 0–300 |

**Integration tests** (`test_api_integration.py`)

| Area | What is checked |
|---|---|
| Basics | Health check; 6 default rules; frontend, JS and CSS served; 6 villages and 3 DEMO pregnancies seeded |
| Registration | Due date = LMP + 280 days; 4 visits numbered 1–4 with the first at week 12; registration SMS sent; record saved. Edge cases: LMP today and exactly 280 days ago accepted (the latter gets one visit, today); 281 days ago and a future LMP rejected; unknown village, a doctor or unknown user as ASHA worker, bad phone, age 11/56 rejected; duplicate active phone (including a DEMO mother's) rejected with `409` |
| Recording visits | High BP flags high risk, alerts the doctor and texts the next visit date; normal and moderate readings send no alert; the same visit cannot be recorded twice (`409`); the last visit sends the "last visit" SMS; unknown visit `404`; out-of-range or missing readings `422`; a new high reading reopens an already reviewed case |
| Doctor reviews | Each decision texts the right people (routine: nobody; PHC visit: mother; refer: mother; the ASHA worker always); note is trimmed; non-doctor, unknown user, bad decision, empty note rejected; unknown pregnancy `404` |
| Risk rules | Raising the systolic threshold to 145 turns the same reading (142) from high to normal; unknown rule `404`; out-of-range values rejected |
| Lists & summary | Filtering by ASHA worker and status; invalid status `422`; PHC summary counts |
| Reminder job | Reminder sent for a visit today and 3 days away, not 4; running the job twice sends nothing new; a missed visit notifies the mother and the ASHA worker once; recorded visits get no reminder |

**Known gap (marked `xfail`):** a doctor's note made only of spaces passes validation and is saved as empty text. The frontend blocks it, but the API does not. It appears in the results as an expected failure (`x`) rather than a failure, so it stays documented until it is fixed.

### Results

Run `python -m pytest -v`, then replace this block with the summary line and the date:

```
Last run: <date>, <macOS version>, Python <version>
<paste the final summary line here, e.g. "N passed, 1 xfailed in X.XXs">
```

To save the full output for a report:

```bash
python -m pytest -v | tee test-results.txt
```

Optional coverage report, showing which backend lines the tests executed:

```bash
python -m pip install pytest-cov
python -m pytest --cov=backend --cov-report=term-missing
```

## Demo scenarios

Use these walkthroughs to demonstrate how the frontend and backend work together. Seeded patient names and measurements are fictional demo data, not real health records.

1. **Explore localized village data:** Open the ASHA screen, switch to Gujarati, and view the mothers. Village labels come from the API-backed village table. Open **Register pregnant woman** to see the supported village list; switch back to English and the same entries change language.
2. **Register a pregnancy:** Submit the registration form with a supported village and a unique phone number. The API stores the mother and pregnancy, calculates the EDD, schedules ANC visits, and adds a registration entry to the SMS log. Reload the page to confirm the record persisted.
3. **Record a high-risk visit:** Open a scheduled visit and enter systolic BP `146`, diastolic BP `94`, Hb `10.9`, and a weight. The backend stores the readings, applies the editable risk rules, flags the case for doctor review, and logs a simulated alert. Switch to the Doctor screen to review and save a referral or PHC decision.
4. **Run visit reminders:** Open the SMS log and select **Run daily reminder job**. Visits due within three days produce a reminder; overdue visits produce notices for the mother and ASHA worker. Run the job again the same day to show it avoids duplicate notices.
5. **Change a risk threshold:** Open the PHC admin screen and change a rule value. The backend persists the new value and risk assessments use it when the page reloads.

The notification service is a local simulation: it persists message records in the SMS log but does not send texts to phones.

## Next steps

- Real login with role-based access
- SMS gateway integration for reminders and alerts
- Offline data entry and sync for ASHA workers (NFR3)

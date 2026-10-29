# Maternal Care Coordinator: Test Descriptions

## Unit tests

Unit tests call one function or schema directly with fixed inputs, with no server involved.

### test\_visit\_status.py

1. `test_unrecorded_visit_status_by_distance`: an unrecorded visit is missed if its date has passed, due from today up to 7 days ahead, and upcoming from 8 days.
2. `test_recorded_visit_is_always_done`: a recorded visit counts as done whatever its scheduled date was.
3. `test_defaults_to_real_today_when_no_date_given`: without a date passed in, the function uses today's real date.

### test\_schedule.py

4. `test_early_registration_gets_all_four_visits_on_the_national_weeks`: an early registration gets visits at weeks 12, 20, 28 and 36.
5. `test_registration_on_the_lmp_day_gets_four_visits`: registering on the LMP day still schedules all four visits.
6. `test_registration_exactly_at_week_12_puts_first_visit_today`: registering exactly at week 12 puts the first visit today.
7. `test_late_registration_moves_first_visit_to_today_not_the_past`: a late registration moves the first visit to today instead of a past date.
8. `test_visit_too_close_to_the_first_one_is_skipped`: a visit only a week after the first one is dropped.
9. `test_gap_of_exactly_14_days_is_not_enough`: a visit exactly 14 days after the previous one is dropped.
10. `test_gap_of_15_days_is_enough`: a visit 15 days after the previous one is kept.
11. `test_very_late_registration_gets_one_visit_today`: registering at week 35 or 39 gives just one visit, today.
12. `test_no_later_visit_on_or_after_the_due_date`: no later visit is scheduled on or after the due date.
13. `test_visit_one_day_before_the_due_date_is_kept`: a visit one day before the due date is kept.
14. `test_today_defaults_to_the_real_today`: without a date passed in, scheduling uses today's real date.
15. `test_schedule_rules_hold_for_every_week_of_pregnancy`: for every registration week from 0 to 39, visits are never in the past, are more than 14 days apart, and fall before the due date.

### test\_risk.py

16. `test_rule_boundaries`: each risk threshold is checked just below and exactly at its limit (BP, Hb, age), plus several problems at once.
17. `test_high_systolic_and_diastolic_give_two_hits`: high systolic and diastolic BP both trigger their own rule.
18. `test_hit_reports_the_reading_that_tripped_it`: a triggered rule reports which rule fired and the reading that caused it.
19. `test_without_a_visit_only_age_is_checked`: before any visit is recorded, only the mother's age is checked.
20. `test_edited_threshold_is_used_straight_away`: changing a threshold takes effect immediately.
21. `test_no_visits_and_normal_age_is_normal`: with no visits and a normal age, the risk is normal.
22. `test_no_visits_but_age_over_35_is_moderate`: a mother over 35 is moderate risk even before any visit.
23. `test_high_beats_moderate`: when high and moderate rules both fire, the overall level is high.
24. `test_reasons_are_not_repeated`: "High BP" is listed once even when both BP rules fire.
25. `test_only_the_latest_recorded_visit_counts`: an old high reading no longer counts once a newer visit is normal.
26. `test_latest_means_highest_visit_number_not_list_order`: the latest visit is chosen by visit number, not by its position in the list.
27. `test_unrecorded_visits_are_ignored`: readings on a visit that hasn't been recorded are ignored.

### test\_schemas.py

28. `test_valid_indian_mobile_numbers`: 10-digit numbers starting with 6–9 are accepted.
29. `test_invalid_mobile_numbers_are_rejected`: numbers with a wrong first digit, wrong length, letters, a +91 prefix or nothing at all are rejected.
30. `test_age_limits_are_allowed`: ages 12 and 55 are accepted.
31. `test_age_outside_limits_is_rejected`: ages 11, 56 and −1 are rejected.
32. `test_name_can_be_given_in_both_languages`: a name can be given in both English and Gujarati.
33. `test_blood_group_defaults_to_unknown`: blood group is "Unknown" if not given.
34. `test_empty_village_is_rejected`: an empty village is rejected.
35. `test_gravida_and_parity_default_to_first_pregnancy`: gravida and parity default to a first pregnancy (G1 P0).
36. `test_invalid_pregnancy_fields_are_rejected`: gravida 0, negative parity and an invalid date are rejected.
37. `test_readings_at_the_limits_are_accepted`: BP, Hb, weight and notes are accepted at their exact limits.
38. `test_readings_outside_the_limits_are_rejected`: readings one step past their limits, and fractional BP, are rejected.
39. `test_every_reading_is_required`: a visit missing any reading is rejected.
40. `test_notes_are_optional`: a visit can be saved without notes.
41. `test_the_three_decisions_are_accepted`: the three doctor decisions are accepted.
42. `test_invalid_reviews_are_rejected`: unknown decisions and empty or overlong notes are rejected.
43. `test_rule_values_in_range_are_accepted`: rule values from 0 to 300 are accepted.
44. `test_rule_values_out_of_range_are_rejected`: rule values below 0 or above 300 are rejected.

## Integration tests

Integration tests send real HTTP requests through FastAPI, validation, domain logic and the database (`test_api_integration.py`).

45. `test_health_check_and_default_rules`: the API is up and has the 6 default risk rules.
46. `test_frontend_is_served_by_backend`: the backend serves the web page, JavaScript and CSS.
47. `test_seeded_villages_and_demo_records`: the 6 villages and 3 DEMO pregnancies are seeded.
48. `test_registration_creates_record_schedule_and_sms`: registration calculates the due date, schedules 4 visits and sends a registration SMS.
49. `test_registration_persists`: a registered mother can be fetched again afterwards.
50. `test_very_late_registration_gets_one_visit_today`: registering at exactly 40 weeks gives one visit, today.
51. `test_registration_validation`: valid and invalid registrations (LMP date limits, village, ASHA worker, phone, age) get the right response.
52. `test_duplicate_active_phone_is_rejected`: a phone number that already has an active pregnancy is rejected.
53. `test_demo_mothers_phone_counts_as_duplicate`: a DEMO mother's phone number also counts as a duplicate.
54. `test_different_phone_registers_fine`: a second mother with a different phone registers fine.
55. `test_high_risk_visit_is_flagged_and_doctor_alerted`: a high-BP visit is flagged high risk, alerts the doctor and texts the mother her next date.
56. `test_normal_visit_sends_no_alert`: a normal visit sends no alert to the doctor.
57. `test_moderate_visit_goes_on_watch_list_without_alert`: low Hb gives moderate risk without an alert.
58. `test_same_visit_cannot_be_recorded_twice`: the same visit can't be recorded twice.
59. `test_last_visit_sends_the_last_visit_message`: recording the final visit sends the "last visit" SMS.
60. `test_unknown_visit_is_404`: recording a visit that doesn't exist returns 404.
61. `test_invalid_readings_are_rejected`: out-of-range or missing readings are rejected.
62. `test_new_high_reading_reopens_a_reviewed_case`: a new high reading puts an already reviewed case back in the doctor's queue.
63. `test_review_decision_notifies_the_right_people`: each doctor decision texts the right people, and the review is saved.
64. `test_invalid_reviews_are_rejected`: reviews from non-doctors, with bad decisions or with empty notes are rejected.
65. `test_review_for_unknown_pregnancy_is_404`: a review for a pregnancy that doesn't exist returns 404.
66. `test_whitespace_only_note_is_rejected`: a note made only of spaces should be rejected (known gap, marked expected to fail).
67. `test_changing_a_threshold_changes_the_next_assessment`: raising the BP threshold turns the same reading from high to normal.
68. `test_unknown_rule_is_404`: editing a rule that doesn't exist returns 404.
69. `test_rule_value_out_of_range_is_rejected`: rule values outside 0–300 are rejected.
70. `test_pregnancy_list_filters`: the pregnancy list filters correctly by ASHA worker and status.
71. `test_summary_counts`: the PHC summary counts pregnancies, visits and high-risk cases correctly.
72. `test_reminder_window`: reminders go out for visits 0–3 days away but not 4.
73. `test_reminder_job_is_idempotent`: running the reminder job twice doesn't send duplicate reminders.
74. `test_missed_visit_notifies_mother_and_asha_once`: a missed visit notifies the mother and the ASHA worker exactly once.
75. `test_recorded_visit_gets_no_reminder`: a visit that's already recorded gets no reminder.

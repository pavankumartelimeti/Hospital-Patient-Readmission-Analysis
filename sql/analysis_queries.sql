-- ============================================================
-- Hospital Patient Readmission Analysis - SQL Queries
-- Database: hospital.db (SQLite)
-- Author: [Your Name]  |  Project: Resume Portfolio
-- ============================================================

-- ============================================================
-- 1. OVERALL READMISSION RATE
-- ============================================================
SELECT
    COUNT(*)                                          AS total_patients,
    SUM(readmitted_30day)                             AS total_readmitted,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct
FROM patients;


-- ============================================================
-- 2. READMISSION RATE BY DIAGNOSIS (ranked worst to best)
-- ============================================================
SELECT
    primary_diagnosis,
    COUNT(*)                                          AS patient_count,
    SUM(readmitted_30day)                             AS readmitted_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                     AS avg_length_of_stay,
    ROUND(AVG(num_medications), 1)                    AS avg_medications
FROM patients
GROUP BY primary_diagnosis
ORDER BY readmission_rate_pct DESC;


-- ============================================================
-- 3. READMISSION RATE BY AGE GROUP
-- ============================================================
SELECT
    CASE
        WHEN age < 30 THEN '18-29'
        WHEN age < 45 THEN '30-44'
        WHEN age < 60 THEN '45-59'
        WHEN age < 75 THEN '60-74'
        ELSE '75+'
    END                                               AS age_group,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                     AS avg_los
FROM patients
GROUP BY age_group
ORDER BY MIN(age);


-- ============================================================
-- 4. INSURANCE TYPE IMPACT ON READMISSION
-- ============================================================
SELECT
    insurance_type,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                     AS avg_los,
    ROUND(AVG(num_medications), 1)                    AS avg_medications
FROM patients
GROUP BY insurance_type
ORDER BY readmission_rate_pct DESC;


-- ============================================================
-- 5. DISCHARGE DISPOSITION IMPACT
-- ============================================================
SELECT
    discharge_disposition,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                     AS avg_los
FROM patients
GROUP BY discharge_disposition
ORDER BY readmission_rate_pct DESC;


-- ============================================================
-- 6. HIGH-RISK PATIENT PROFILE
--    (multiple diagnoses + high medications + prior admissions)
-- ============================================================
SELECT
    patient_id,
    age,
    primary_diagnosis,
    num_diagnoses,
    num_medications,
    num_prior_admissions,
    length_of_stay,
    discharge_disposition,
    readmitted_30day
FROM patients
WHERE
    num_diagnoses >= 4
    AND num_medications >= 10
    AND num_prior_admissions >= 2
ORDER BY num_prior_admissions DESC, num_medications DESC
LIMIT 20;


-- ============================================================
-- 7. MONTHLY ADMISSIONS TREND (2022-2024)
-- ============================================================
SELECT
    SUBSTR(admission_date, 1, 7)                      AS year_month,
    COUNT(*)                                          AS admissions,
    SUM(readmitted_30day)                             AS readmissions,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct
FROM patients
GROUP BY year_month
ORDER BY year_month;


-- ============================================================
-- 8. GENDER AND RACE BREAKDOWN
-- ============================================================
SELECT
    gender,
    race,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct,
    ROUND(AVG(length_of_stay), 1)                     AS avg_los
FROM patients
GROUP BY gender, race
ORDER BY readmission_rate_pct DESC;


-- ============================================================
-- 9. CORRELATION: LENGTH OF STAY vs READMISSION
-- ============================================================
SELECT
    CASE
        WHEN length_of_stay <= 2  THEN '1-2 days'
        WHEN length_of_stay <= 5  THEN '3-5 days'
        WHEN length_of_stay <= 10 THEN '6-10 days'
        ELSE '10+ days'
    END                                               AS los_bucket,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct
FROM patients
GROUP BY los_bucket
ORDER BY MIN(length_of_stay);


-- ============================================================
-- 10. TOP RISK COMBINATIONS (Diagnosis + Insurance)
-- ============================================================
SELECT
    primary_diagnosis,
    insurance_type,
    COUNT(*)                                          AS patient_count,
    ROUND(AVG(readmitted_30day) * 100, 2)             AS readmission_rate_pct
FROM patients
GROUP BY primary_diagnosis, insurance_type
HAVING patient_count >= 30
ORDER BY readmission_rate_pct DESC
LIMIT 15;

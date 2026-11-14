# CareIG Specialty Pharmacy

## CareIG Specialty Pharmacy

## Standard Operating Procedure

## IVIG Home Infusion — Intake to Billing

**v5.0**

Document #: | CareIG-SOP-BILL-001  
---|---  
Version: | 5.0  
Effective: | March 23, 2026  
Owner: | Director of Revenue Cycle Management  
EIN: | 47-3821056  
NPI: | 1234567893  
  
## Table of Contents

  1. Overview & Purpose

  2. Roles & File Access

  3. File System Structure

  4. Global Rules

  5. Workflow Summary

  6. Intake

  7. Benefits Verification & Drug Source Decision

  8. Prior Authorization

  9. Clinical Scheduling & Visit Documentation



  * 10.Billing & Payment Posting

  * 11.Denial Management & Appeals

  * 12.Escalation & Monitoring

  * 13.Reference Tables

  * 14.Appendix A — Scripts & Templates




# 1\. Overview & Purpose

This SOP governs the end-to-end IVIG home infusion process at CareIG Specialty Pharmacy — from referral receipt through claim payment. All staff performing intake, benefits verification, prior authorization, clinical scheduling, or billing must follow this document. It references standard tools including spreadsheets, email, Slack, shared file storage, and calendar. No proprietary EHR, clearinghouse portal, or payer portal is required.

All case data lives under a case folder named CASE_ID (format: LastName_MMDDYYYY), where the date is the patient’s DOB. This CASE_ID is used in all audit log entries, Slack posts, and file references throughout this SOP. Team communications use defined Slack channels. Claims are submitted by email with PDF attachments. All major actions are logged to audit_log.xlsx. For any date you write in files, use the YYYY-MM-DD format, except if specified otherwise.

Covered drugs: Gammaplex, Octagam, Gammagard S/D, Gammagard Liquid, Privigen, Gamunex-C, Hizentra, HyQvia.

If you encounter a situation not covered by this SOP, do not guess. Stop work on that step, note what happened in audit_log.xlsx, and contact your direct supervisor immediately using the escalation path in Section 12. When in doubt, always escalate before acting.

# 2\. Roles & File Access

Role | Writes To | Reads From  
---|---|---  
Patient Representative | intake.xlsx |   
Benefits Verification Specialist (BVS) | benefits.xlsx, auth.xlsx, | intake.xlsx, payer_rules.xlsx  
Clinical Coordinator | clinical.xlsx | auth.xlsx, benefits.xlsx  
Infusion Nurse | visit_note.xlsx | clinical.xlsx  
Billing Specialist | claim.xlsx, , | visit_note.xlsx, auth.xlsx, benefits.xlsx,  
AR Specialist | claim.xlsx (payment cols) | claim.xlsx, payer_rules.xlsx  
Director of Revenue Cycle | All files | All files — approves write-offs >$200 and collections referrals  
  
Any file access outside the above scope must be logged to audit_log.xlsx (Action = Out-of-Scope Access) and reported to compliance@careig.com.

# 3\. File System Structure

File Name | Purpose  
---|---  
intake.xlsx | Patient demographics, insurance, consent status, contact log, contraindications  
benefits.xlsx | BV results: coverage, deductible, OOP, PA contacts, nursing code preference, call log  
auth.xlsx | PA details: submission date, PA number, approval/denial status, expiry, follow-up log  
clinical.xlsx | Drug source, supply checklist, nurse assignment, visit date/time  
visit_note.xlsx | Nurse documentation: drug, dose, lot, NDC, times, pre-meds, saline, vitals, signature  
claim.xlsx | Claim: codes, units, ICD-10, PA number, submission log, payment fields  
DENIAL_[CARC]_[DOS].xlsx | One file per denial: CARC code, action, appeal status  
appeals_log.xlsx | Appeal level, submitted date, decision, follow-up log  
Workspace (PDFs) | PDFs: LMN, PA approval, EOB, labs, consent, claim export, statements  
audit_log.xlsx | Global audit trail — see Section 4 for columns. Append-only.  
jcodes.xlsx | J-codes and nursing codes (read-only)  
payer_rules.xlsx | Payer rules: contracted rates, timely filing limits, nursing code pref, formulary, claim/appeal addresses  
Template files | Blank form masters — copy to docs/ before use, never edit in place  
  
# 4\. Global Rules

DOS (Date of Service) refers to the date the patient received the infusion visit.

## 4.1 Audit Logging

Append one row to audit_log.xlsx at each major checkpoint. Columns: Date | CASE_ID | Action | File_Updated | Field_Updated | New_Value | Staff_User | Result (SUCCESS / FAILED / STOP — reason). Do not log every substep — only the checkpoints called out in each section.

The Stop Protocol (Section 4.2) is itself a checkpoint — always log a stop event when triggered, even though it is not listed as a checkpoint within a specific workflow section.

## 4.2 Stop Protocol

When a validation condition fails: note the reason in audit_log.xlsx with action ‘Stop Protocol’ and columns File_Updated, Field_Updated, and New_Value set to N/A, and hold the case until the issue is resolved. Do not move to the next step until your supervisor or the responsible team member confirms the issue has been cleared.

## 4.3 Prohibited Actions

  * Do not bill any IVIG drug J-code when clinical.xlsx col Drug_Source ≠ CareIG.

  * Do not bill pre-medication J-codes unless visit_note.xlsx col Premeds_Administered documents drug, dose, route, time, and indication.

  * Do not use ordered dose for unit calculations — always use visit_note.xlsx col Dose_Administered_Grams.

  * Do not submit a claim when claim.xlsx already has Submission_Date populated for the same DOS.

  * Do not write off any balance >$200 without Director of Revenue Cycle approval (Slack #billing-mgmt).



  * Do not respond to legal threats or attorney communications — post to #compliance immediately.

  * Do not assign an ICD-10 code not supported by the physician's documentation and the PA approval.




## 4.4 Phone Call Workaround

When a step requires a phone call, check whether the required information has already been provided via email, referral document, or another input file. If the information is already available, proceed using that source and log the source in the relevant call log field, if appropriate. If the information is not available and a call cannot be made, follow the Stop Protocol (Section 4.2).

# 5\. Workflow Summary

# | Action | File Written | Slack (if required)  
---|---|---|---  
1 | Referral received → create → populate intake.xlsx | intake.xlsx | —  
2 | Patient contacted → consent form sent | intake.xlsx: Consent_Status = Form Sent | —  
3 | Signed consent received → BVS assigned | intake.xlsx: Consent_Status = Signed, BVS_Assigned | #intake-team: [BVS ASSIGNED] CASE_ID | Payer | Drug  
4 | BVS completes BV + drug source decision + patient financial counseling | benefits.xlsx: BV_Complete = YES; clinical.xlsx: Drug_Source | —  
5 | BVS checks formulary → submits PA | auth.xlsx: PA_Submission_Date, PA_Status = Pending | #intake-team: [PA SUBMITTED] CASE_ID | Payer | Drug  
6 | PA approved → clinical handoff | auth.xlsx: PA_Status = Approved; clinical.xlsx: Handoff_Status = Received | #clinical-scheduling: [PA APPROVED] CASE_ID | Drug | Dose | PA# | Exp  
7 | Supply checklist complete → nurse scheduled | clinical.xlsx: Visit_Date, Nurse_Assigned | #clinical-scheduling: [SCHEDULED] CASE_ID | Date | Nurse  
8 | Nurse completes visit → signs visit note | visit_note.xlsx: Nurse_Signature | #clinical-scheduling: [VISIT COMPLETE] CASE_ID | DOS  
9 | Billing validates → builds → submits claim | claim.xlsx: Submission_Date, Claim_Status = Submitted | #billing: [CLAIM SUBMITTED] CASE_ID | DOS | Payer | $Amount  
10 | ERA/EOB posted → payment or denial actioned | claim.xlsx: Payment_Posted_Date or file | If denial: #billing-appeals: [DENIAL] CASE_ID | CARC  
  
# 6\. Intake

## 6.1 Case Setup

  1. Copy intake_blank.xlsx to create intake.xlsx for this case.

  2. Populate intake.xlsx from the referral document. Required fields:


intake.xlsx Column | Source | Required  
---|---|---  
Patient_Last_Name, First_Name, DOB, Address, Phone, Email | Patient fields on referral | Yes (email optional)  
Physician_Name, Physician_NPI, Physician_Email | Physician fields on referral | Yes  
Diagnosis_ICD10 | Diagnosis field on referral | Yes  
Drug_Name, Drug_Dose_Grams, Drug_Frequency | Ordered drug fields (convert dose to grams if in mg) | Yes  
Primary_Insurance_Name, Member_ID, Group_Number, Payer_Phone | Insurance fields | Yes  
Secondary_Insurance_Name, Member_ID | Secondary insurance if listed | No  
Contraindications | Allergies/contraindications from referral | Yes  
Consent_Status | Set to: Pending | Staff sets on creation  
  
**If Physician_NPI is blank after referral entry:** Post to #intake-alerts: [INTAKE HOLD] CASE_ID — Physician NPI missing. Email a request for infomation to intake.xlsx col Physician_Email. Do not proceed.

Log to audit_log.xlsx: Action = Referral Received.

## 6.2 Patient Contact

  3. Call patient at intake.xlsx col Patient_Phone. Verbatim script:


  * "Hello, may I speak with [Patient Name]? This is [Your Name] from CareIG Specialty Pharmacy. Dr. [Physician_Name] has referred you for home IVIG infusion therapy. I'm calling to verify your information and explain next steps. Do you have a few minutes?"


  4. If no answer, leave this voicemail verbatim — do not state the diagnosis:


  * "Hello, this is [Your Name] from CareIG Specialty Pharmacy at [Phone]. We received a referral from your physician. Please call us back at your convenience. Thank you."


  5. Log each attempt in intake.xlsx col Contact_Attempt_Log: [Date] [Time] — [Reached / No Answer / Voicemail].



**If Contact_Attempt_Log has 3 entries and none is Reached:** Post to #intake-alerts: [UNREACHABLE] CASE_ID — 3 failed attempts. Complete Template 1 and email to intake.xlsx col Physician_Email. Do not proceed.

  6. When patient is reached: confirm demographics, explain the consent requirement, and email the consent form to intake.xlsx col Patient_Email. Subject: CareIG — Consent Form Required | [Patient Last Name]. If no email is on file, mail the form to intake.xlsx col Patient_Address and note the method in the Contact_Attempt_Log. Set intake.xlsx col Consent_Status = Form Sent.


  * "Before we schedule your visit, a signed Consent for Treatment and Financial Responsibility form is required. Once we verify your insurance, we will also contact you with your estimated out-of-pocket costs before scheduling."


  7. When signed consent is received: save as consent_signed.pdf. Set Consent_Status = Signed.

  8. Assign BVS. Set intake.xlsx col BVS_Assigned. Post to #intake-team: [BVS ASSIGNED] [CASE_ID] | Payer: [Insurance_Name] | Drug: [Drug_Name] | Dose: [Drug_Dose_Grams]g.




**If BVS attempts BV and intake.xlsx col Consent_Status ≠ Signed:** Post to #intake-alerts: [CONSENT MISSING] CASE_ID. Do not begin BV.

Log to audit_log.xlsx: Action = BVS Assigned.

# 7\. Benefits Verification & Drug Source Decision

## 7.1 Benefits Verification

BVS calls the payer at intake.xlsx col Primary_Payer_Phone. Populate all required fields in benefits.xlsx. Do not set BV_Complete = YES until every required field is non-blank.

benefits.xlsx Column | How to Obtain | Req.  
---|---|---  
Home_Infusion_Covered | Ask: 'Does this plan cover home infusion therapy?' | Yes  
Benefit_Type | Ask: 'Is IVIG under the medical or pharmacy benefit?' | Yes  
PA_Required, PA_Phone, PA_Submission_Email | Ask if PA is required and get phone number and email submission address | Yes (if PA required)  
Specialty_Pharmacy_Require d, Specialty_Pharmacy_Name | Ask if a specific specialty pharmacy is required | Yes  
CareIG_Network_Status | Ask: 'Is CareIG Specialty Pharmacy NPI [NPI] in-network?' | Yes  
Deductible_Individual, Deductible_Met_YTD | Individual deductible and amount met YTD | Yes  
OOP_Max_Individual, OOP_Max_Met_YTD | Out-of-pocket maximum and amount met YTD | Yes  
Coinsurance_Pct, Copay_Amount | Coinsurance percentage and per-visit copay | Yes  
Plan_Year_Type | Calendar or fiscal year | Yes  
Payer_Type | Classify: Medicare Part B / Medicare Adv. / Medicaid / Commercial PPO / Commercial HMO | Yes  
Nursing_Code_Pref | Determine from payer_rules.xlsx: 99600 / G0153 / T1029 / T1032 | Yes  
Coverage_Effective Date, Coverage Term Date | Ask: ‘What is the coverage effective date and termination date for this plan?’ Enter both as MM/DD/YYYY. | Yes  
BV_Call_Date, BV_Rep_Name, BV_Call_Ref_Number | Document every call — mandatory | Yes  
BV_Complete | Set YES only after all required fields are non-blank — set last | Yes  
  
Log to audit_log.xlsx: Action = BV Complete.

## 7.2 Drug Source Decision

Immediately after BV, write the drug source to clinical.xlsx col Drug_Source:

  * CareIG_Network_Status = In-Network AND Specialty_Pharmacy_Required = NO → Drug_Source = CareIG.

  * CareIG_Network_Status = Out-of-Network AND Specialty_Pharmacy_Required = YES → Drug_Source = value from benefits.xlsx col Specialty_Pharmacy_Name (e.g., Accredo). CareIG bills nursing and supplies only — do not bill any IVIG drug J-code on the CareIG claim.

  * CareIG_Network_Status = Out-of-Network AND Specialty_Pharmacy_Required = NO → Post to #intakemgmt: [OON NO PREFERRED PHARMACY] CASE_ID — CareIG is out-of-network but payer has no required specialty pharmacy. Supervisor must determine next step (single-case agreement, patient referral, or self-pay). Do not proceed until Drug_Source is confirmed by supervisor.

  * Benefit_Type = Pharmacy → post to #billing-mgmt: [BENEFIT TYPE ISSUE] CASE_ID — IVIG under pharmacy benefit. Awaiting Director guidance. Do not proceed until resolved.

  * CareIG_Network_Status = In-Network AND Specialty_Pharmacy_Required = YES → Drug_Source = value from benefits.xlsx col Specialty_Pharmacy_Name. CareIG bills nursing and supplies only. Do not bill any IVIG drug J-code on the CareIG claim."




## 7.3 Patient Financial Counseling

Before making this call, calculate the patient’s estimated out-of-pocket using benefits.xlsx. Add together any remaining deductible (Deductible_Individual minus Deductible_Met_YTD), then apply the Coinsurance_Pct to the expected billed amount, and add the Copay_Amount if applicable. To estimate the billed amount, look up the ordered drug's J-code in fee_schedule.xlsx col Billed_Rate, multiply by the expected units, and add the estimated nursing and supply charges from the same file. Use that dollar figure in the script below.

"[Patient Name], this is [Your Name] from CareIG. I’ve had a chance to review your insurance benefits. Based on your current plan, your estimated out-of-pocket cost per infusion visit is approximately $[dollar amount you calculated]. Keep in mind this is an estimate — your insurance company determines the final amount once the claim is processed. Do you have any questions about that?"

Log call in benefits.xlsx col Financial_Counseling_Log: [Date] [Time] — [outcome]. If patient reports hardship: set intake.xlsx col Financial_Hardship = YES and post to #intake-team: [FINANCIAL HARDSHIP] CASE_ID — refer to Patient Assistance Program.

# 8\. Prior Authorization

If benefits.xlsx col PA_Required = NO, skip Sections 8.1 through 8.5. Proceed directly to Section 8.6 (Clinical Handoff), setting auth.xlsx col PA_Status = Not Required and PA_Number = N/A.

## 8.1 Formulary Check

Before submitting any PA, confirm the ordered drug is covered on the payer's formulary. Open payer_rules.xlsx. Read the row for the payer (benefits.xlsx col Primary_Insurance_Name). Check col Formulary_Covered_Drugs.

**If the ordered drug (intake.xlsx col Drug_Name) is not listed in payer_rules.xlsx col Formulary_Covered_Drugs for the payer:**

Contact prescribing physician via phone to intake.xlsx col Physician_Phone to request either an alternative covered drug or a written formulary exception letter. Do not submit PA until one of the two paths below is confirmed. After reaching the physician, or if they could not be reached and the issue is still present, post to #intake-team: [FORMULARY ISSUE] CASE_ID | Drug: [Drug_Name] | Payer: [Insurance_Name]. Exception: if the physician's guidance is already on file (Section 4.4) and the issue is resolved by applying it (e.g. an email authorizing substitution of a covered drug), proceed using that guidance and do not post the [FORMULARY ISSUE] notice.

If the physician provides a formulary exception letter: save it as formulary_exception.pdf, document the basis in auth.xlsx col Formulary_Exception_Notes, and include it in the PA packet. Proceed to Section 8.2. If the physician substitutes an alternative covered drug: update intake.xlsx col Drug_Name with the new drug and restart Section 8.1. If neither is provided within 2 business days: post to #intake-mgmt: [FORMULARY UNRESOLVED] CASE_ID and hold the case.

## 8.2 Required PA Documents

All of the following must be saved in the case folder before PA submission:

  * PA request form (payer-specific) — pa_form_[PayerName].pdf

  * Physician Letter of Medical Necessity — signed, on letterhead, dated within 90 days — lmn_[PhysicianName].pdf

  * Most recent IgG lab result (if applicable) — igglevel_[MMDDYYYY].pdf

  * Most recent physician progress note — progress_note_[MMDDYYYY].pdf

  * Formulary exception documentation (if applicable) — formulary_exception.pdf




**If any required document above is missing or invalid :**

Post to #intake-alerts: [PA HOLD] CASE_ID — [missing / invalid]: [document name]. Do not submit, and follow 4.2 with reason “invalid file”

## 8.3 PA Submission

  9. Email to payer PA address (payer_rules.xlsx col PA_Submission_Email). Subject: [PA REQUEST] CareIG | [Patient Last Name] | MemberID: [Member_ID] | Drug: [Drug_Name] | Dose: [Drug_Dose_Grams]g | Dx: [Diagnosis_ICD10]. Attach all required PA documents.

  10. Update auth.xlsx: PA_Submission_Date = today, PA_Status = Pending, Last_Followup_Date = today.

  11. Post to #intake-team: [PA SUBMITTED] [CASE_ID] | Payer: [name] | Drug: [Drug_Name].




Log to audit_log.xlsx: Action = PA Submitted.

## 8.4 PA Follow-Up

Every business day while a PA is pending, open auth.xlsx and check col PA_Status. If the status is still Pending and (today’s date minus Last_Followup_Date) is 2 or more days, call the payer PA line (benefits.xlsx col PA_Phone). Append a note to auth.xlsx col PA_Call_Log: [Date] [Time] | Rep: [name] | Status: [status] | Next expected update: [date]. Update Last_Followup_Date to today.

If still Pending after 5 days from PA_Submission_Date: post to #intake-mgmt: [PA DELAY] [CASE_ID] | Payer: [name] | Days Pending: [count].

## 8.5 Peer-to-Peer (P2P) Request

If payer offers a P2P review after denial:

  12. Call payer, obtain time slots, record in auth.xlsx col P2P_Available_Slots.

  13. Complete Template 2 (Appendix A). Save as p2p_request.pdf. Email to intake.xlsx col Physician_Email. Subject: [P2P REQUEST] [CASE_ID] | [Payer].

  14. Set auth.xlsx col P2P_Status = Requested, P2P_Request_Date = today.




**If P2P_Status = Requested AND P2P_MD_Response_Date is blank AND (today − P2P_Request_Date) ≥ 2 days:** Post to #intake-alerts: [P2P NO RESPONSE] CASE_ID. Set P2P_Status = No Response. Proceed to Level 1 appeal (Section 11).

## 8.6 PA Approval — Clinical Handoff

  15. Save PA approval as pa_approval_[PayerName].pdf. Update auth.xlsx: PA_Number, PA_Approved_Drug, PA_Approved_Dose, PA_Approved_Frequency, PA_Effective_Date, PA_Expiration_Date, PA_Status = Approved.

  16. Update clinical.xlsx: Handoff_Status = Received, PA_Number, PA_Expiration_Date.

  17. Post to #clinical-scheduling: [PA APPROVED] [CASE_ID] | Drug: [PA_Approved_Drug] | Dose:



  * [PA_Approved_Dose]g | PA#: [PA_Number] | Exp: [PA_Expiration_Date] | Drug Source: [Drug_Source].



**If PA_Approved_Drug does not match intake.xlsx col Drug_Name (case-insensitive):** Post to #intake-alerts: [PA DRUG MISMATCH] CASE_ID | Ordered: [Drug_Name] | Approved: [PA_Approved_Drug]. Resolve with payer before scheduling.

**If auth.xlsx col PA_Approved_Dose is less than intake.xlsx col Drug_Dose_Grams:**

Post to #intake-alerts: [PA DOSE MISMATCH] CASE_ID | Ordered: [Drug_Dose_Grams]g | Approved: [PA_Approved_Dose]g. Do not schedule. BVS must contact payer to request approval for the full ordered dose before proceeding.

Log to audit_log.xlsx: Action = PA Approved — Clinical Handoff.

## 8.7 PA Denial

  18. Update auth.xlsx: PA_Denial_Date = today, PA_Denial_Reason = denial text, PA_Status = Denied.

  19. Post to #billing-appeals: [PA DENIED] [CASE_ID] | Payer: [name] | Reason: [PA_Denial_Reason]. Proceed to Section 11 for appeal.




Log to audit_log.xlsx: Action = PA Denied.

# 9\. Clinical Scheduling & Visit Documentation

## 9.1 Supply Checklist

Before scheduling the nurse visit, confirm all items below are completed in clinical.xlsx. All columns except NS_500mL_Qty_Ordered should contain YES. NS_500mL_Qty_Ordered must contain a number (integer) of 2 or more:

clinical.xlsx Column | Requirement  
---|---  
Drug_Order_Placed | Drug ordered from CareIG or partner pharmacy per Drug_Source  
Drug_Delivery_Confirmed | Delivery confirmed at patient address — record delivery date  
Drug_Lot_Number, Drug_NDC | Lot number and NDC received from dispensing pharmacy  
NS_500mL_Qty_Ordered | Enter the number of 500 mL NS bags ordered (integer), minimum 2. If the ordered drug is Gammaplex, enter 0 and order 500 mL 10% Dextrose bags instead (minimum 2).  
Filter_Tubing_Ordered | 0.2-micron IV filter set ordered (required for all IVIG)  
Benadryl_Available | Diphenhydramine 50 mg/mL vial available if ordered as pre-med (N/A if not ordered)  
Supplies_Other | Gloves, alcohol swabs, dressing kit, sharps container confirmed  
Supply_Checklist_Complete | Set YES only after all above fields are confirmed  
  
**If Supply_Checklist_Complete ≠ YES when nurse scheduling is attempted:**

Post to #clinical-scheduling: [SUPPLY HOLD] CASE_ID — checklist incomplete. Do not schedule until resolved.

## 9.2 Nurse Scheduling

  20. Select nurse matching patient zip code and credential (RN required for first visit; verify state rules in payer_rules.xlsx col Nursing_Credential_Requirement for subsequent visits).

  21. Create calendar event: Title = IVIG Visit — [CASE_ID]. Include nurse.

  22. Set duration using the estimated infusion times in infusion_duration.xlsx. Look up the row matching the ordered drug and dose range to find the estimated visit length in hours.

  23. Confirm visit with patient. Script:



  * "Hello [Patient Name], this is [Your Name] from CareIG. Your insurance has approved your IVIG infusion. We have availability on [Date] at [Time] — does that work for you? The visit will take approximately [X] hours."


  24. Update clinical.xlsx: Visit_Date, Visit_Time, Nurse_Assigned. Post to #clinical-scheduling: [SCHEDULED] [CASE_ID] | Date: [Visit_Date] | Nurse: [Nurse_Assigned].

  25. Email assigned nurse. Subject: [VISIT ASSIGNMENT] [CASE_ID] | [Date]. Include: patient address, drug name, dose, lot number, NDC, infusion rate, pre-med orders, emergency contact, and contraindications from intake.xlsx.




## 9.3 Visit Documentation

The nurse must complete all fields below in visit_note.xlsx and set col Nurse_Signature within 4 hours of visit completion. A claim cannot be initiated if Nurse_Signature is blank.

visit_note.xlsx Column | Description | Required  
---|---|---  
Visit_Date, Visit_Start_Time, Visit_End_Time | Date and exact start/end times | Yes  
Visit_Duration_Minutes | End time − Start time in minutes | Yes  
Drug_Name_Trade, Drug_Name_Generic | E.g., Gammaplex 5% and Immune Globulin Intravenous | Yes  
Drug_NDC, Drug_Lot_Number, Drug_Expiration_Date | Transcribed from vial label | Yes  
---|---|---  
Dose_Ordered_Grams, Dose_Administered_Grams | Ordered vs actual. Claims use Dose_Administered_Grams. | Yes  
Route | IV or SQ — must match MD order | Yes  
Infusion_Start_Rate_mL_hr, Infusion_Rate_Adjustments | Initial rate and all changes with timestamps. If no changes: None. | Yes  
Premeds_Administered | Format: [Drug] [Dose][unit] [Route] at [Time] for [Indication]. If none: None administered. | Yes  
NS_500mL_Bags_Used, NS_250mL_Bags_Used | Count of bags actually used | Yes  
Pump_Used | YES or NO | Yes  
Vital_Signs_Pre, Vital_Signs_Mid, Vital_Signs_Post | BP, HR, Temp, RR at each point. Mid: N/A if no rate changes. | Yes  
Patient_Response | Clinical response. If uneventful: Patient tolerated infusion without adverse events. | Yes  
Education_Provided | Education given. SQ patients: document self- infusion training if performed. If none: None. | Yes  
Nurse_Signature | Full name and credential (e.g., Jane Smith, RN) | Yes — blocks claim if blank  
Dextrose_500mL_Bags_Used | For Gammaplex cases only: number of 500 mL 10% Dextrose bags actually used during the visit. For all other drugs, enter N/A. | Yes for Gammaplex, N/A otherwise.  
  
**If Nurse_Signature is blank:** Post to #clinical-scheduling: [UNSIGNED NOTE] CASE_ID — claim on hold until signed.

Post to #clinical-scheduling: [VISIT COMPLETE] [CASE_ID] | DOS: [Visit_Date]. Log to audit_log.xlsx: Action = Visit Note Signed.

# 10\. Billing & Payment Posting

## 10.1 Pre-Billing Validation

Before building claim.xlsx, confirm every condition below is TRUE. If any is FALSE: post to #billing with the specific failure and do not proceed.

Condition | If FALSE — Post to #billing  
---|---  
visit_note.xlsx col Nurse_Signature is non-blank | [BILLING HOLD — UNSIGNED NOTE] CASE_ID  
auth.xlsx col PA_Status = Approved | [BILLING HOLD — NO PA APPROVAL] CASE_ID  
auth.xlsx col PA_Number is non-blank | [BILLING HOLD — PA NUMBER MISSING] CASE_ID  
auth.xlsx col PA_Expiration_Date ≥ visit_note.xlsx col Visit_Date | [BILLING HOLD — PA EXPIRED ON DOS] CASE_ID | PA Exp: [date] | DOS: [date]  
auth.xlsx col PA_Approved_Drug matches visit_note.xlsx col Drug_Name_Trade (case-insensitive) | [BILLING HOLD — DRUG MISMATCH] CASE_ID | PA: [drug] | Administered: [drug]  
auth.xlsx col PA_Approved_Dose (grams) is greater than or equal to visit_note.xlsx col Dose_Administered_Grams | [BILLING HOLD — DOSE EXCEEDS PA] CASE_ID | PA approved: [PA_Approved_Dose]g | Administered: [Dose_Administered_Grams]g. Post to #billing and escalate to BVS to obtain a revised PA before submitting.  
intake.xlsx col Diagnosis_ICD10 is consistent with PA approval (verify in auth.xlsx) | [BILLING HOLD — ICD10 INCONSISTENT] CASE_ID  
visit_note.xlsx col Dose_Administered_Grams is non-blank and > 0 | [BILLING HOLD — DOSE NOT DOCUMENTED] CASE_ID  
claim.xlsx has no Submission_Date for this DOS (duplicate check) | [DUPLICATE CLAIM RISK] CASE_ID | DOS: [date]  
benefits.xlsx confirms active coverage on DOS | [BILLING HOLD — COVERAGE NOT CONFIRMED] CASE_ID  
  
## 10.2 Claim Construction

Copy claim_blank.xlsx to create claim.xlsx for this case. Use the following rules:

Claim Component | Rule  
---|---  
Drug J-Code | Look up J-code in jcodes.xlsx for Drug_Name_Trade. Units = (Dose_Administered_Grams × 1000) ÷ unit size. See Section 13 for full table and examples. If the result is not a whole number, round down to the nearest integer. Example: 25.3g Privigen = 50,600mg ÷ 500 = 101.2 → bill 101 units.  
Nursing Code | If Visit_Duration_Minutes is 60 or less, bill 99600 × 1 only. Do not bill 99603. Read benefits.xlsx col Nursing_Code_Pref. Blank or 99600: bill 99600 × 1 + 99603 × floor((Visit_Duration_Minutes − 60) ÷ 60). G0153 (Medicare Part B): bill G0153 × 1 only. T1029/T1032: verify per state in payer_rules.xlsx.  
Saline | J7030 × NS_500mL_Bags_Used. J7050 × NS_250mL_Bags_Used. Both from visit_note.xlsx. For Gammaplex cases: do not bill J7030 or J7050. Instead bill A4221 for the Dextrose supply as part of the general infusion supplies line. Read Dextrose_500mL_Bags_Used from visit_note.xlsx to confirm administration was documented before billing.  
Pre-Medications | Parse visit_note.xlsx col Premeds_Administered. Diphenhydramine: J0171 × (mg ÷ 50). Promethazine: J2550 × (mg ÷ 25). If None administered: leave blank.  
Supplies | A4221 × 1 per visit. If Pump_Used = YES: also A4222 × 1.  
Header / Auth Fields | PA_Number = auth.xlsx col PA_Number. Physician_NPI = intake.xlsx col Physician_NPI. CareIG_NPI and Tax_ID from payer_rules.xlsx. DOS = visit_note.xlsx col Visit_Date. ICD10 = intake.xlsx col Diagnosis_ICD10. CareIG Taxonomy Code from org_identifiers.xlsx.  
Split-Bill (OON partner) | If clinical.xlsx col Drug_Source ≠ CareIG: leave all IVIG drug J-code fields blank. Set claim.xlsx col Billing_Model = Split — Drug billed by [Drug_Source].  
Claim_Frequency_C ode | Enter 1 for all original claim submissions. Enter 7 when resubmitting a corrected claim. Enter 8 when voiding a duplicate. Write value to claim.xlsx col Claim_Frequency_Code.  
Modifier | Read visit_note.xlsx col Route. If Route = IV: no modifier required on the drug J- code line. If Route = SQ: append modifier SC to the drug J-code line in claim.xlsx col Drug_Modifier. Write Drug_Modifier to claim.xlsx.  
  
## 10.3 Claim Submission

  26. Export claim.xlsx to PDF → claim_[DOS].pdf.

  27. Email to payer billing address (payer_rules.xlsx col Claim_Submission_Email). Subject: [CLAIM SUBMISSION] CareIG NPI: [NPI] | [Patient Last Name] | MemberID: [Member_ID] | DOS: [Visit_Date]. Attach claim_[DOS].pdf.

  28. Update claim.xlsx: Submission_Date = today, Submission_Ref_Number = email confirmation ID, Claim_Status = Submitted.

  29. Post to #billing: [CLAIM SUBMITTED] [CASE_ID] | DOS: [Visit_Date] | Payer: [name] | Billed: $[Total_Billed].




Log to audit_log.xlsx: Action = Claim Submitted.

## 10.4 ERA & Payment Posting

  30. ERA and EOB documents arrive by email to billing@careig.com from the payer. When received, download the attachment and save it as era_[DOS]_[Payer].pdf.

  31. Compare Paid_Amount to payer_rules.xlsx col Contracted_Rate. If Paid_Amount < Contracted_Rate: post to #billing-mgmt: [UNDERPAYMENT] CASE_ID | Payer: [name] | Expected: $[rate] | Received: $[paid]. Do not write off.

  32. If ERA contains a denial (any CARC-coded line with $0 paid): copy denial_blank.xlsx to create DENIAL_[CARC]_[DOS].xlsx. Populate CARC_Code, Denial_Date, DOS, Denied_Code, Denied_Amount. Follow Section 11.

  33. Update claim.xlsx: Payment_Posted_Date = today, Claim_Status = Paid / Partially Paid / Denied.

  34. If Patient_Responsibility > 0: complete patient_statement_template.docx with patient name, DOS, billed amount, insurance payment, and patient balance. Save as statement_[DOS].pdf. Email to patient at intake.xlsx col Patient_Email. Subject: CareIG Statement of Account | DOS: [Visit_Date].




# 11\. Denial Management & Appeals

## 11.1 Denial Actions by CARC Code

CARC | Denial Reason | Action  
---|---|---  
CO-4 | Procedure code / modifier inconsistent | Correct modifier per visit_note.xlsx col Route. Resubmit.  
CO-11 | Diagnosis inconsistent with procedure | Confirm ICD-10 in claim.xlsx matches PA approval in auth.xlsx. If mismatch: email intake.xlsx col Physician_Email. Subject: [ICD10 CLARIFICATION NEEDED] CASE_ID | DOS: [date]. Body: state the ICD-10 on the claim, the ICD-10 on the PA, and ask the physician to confirm the correct code in writing. Do not resubmit until written confirmation is received and saved to .  
CO-16 | Claim lacks required information | Identify missing field from denial detail (NPI, taxonomy, PA number). Update claim.xlsx. Resubmit.  
CO-18 | Duplicate claim | Check claim.xlsx Submission_Log for prior submission on same DOS. If confirmed duplicate: resubmit the original claim with claim frequency code 8 (void/cancel) via email to the payer billing address. Update claim.xlsx col Claim_Status = Voided. Do not delete the original row. If not: resubmit with frequency code 7.  
CO-22 | COB — other payer may be primary | CO-22 means another payer is primary. Check benefits.xlsx col Secondary_Insurance. If a primary payer is listed that was not yet billed: submit a new claim to that payer first. When their EOB is received, save it as era_[DOS]_[PrimaryPayer].pdf and resubmit to the original payer with COB fields populated: COB_Other_Payer_Name, COB_Other_Payer_Member_ID, COB_Other_Payer_Paid, COB_Other_Payer_EOB_Date.  
CO-50 | Non-covered service | File Level 1 appeal per Section 11.2.  
CO-96 | Non-covered charge | Compare to payer_rules.xlsx contracted rate. If dispute: post to #billing-mgmt. Write-off requires Director approval.  
CO-97 | Benefit not assigned | Open benefits.xlsx col Benefit_Type. If the benefit tier on the original claim does not match what is listed in benefits.xlsx (e.g., billed under pharmacy benefit but should be medical): correct claim.xlsx and resubmit. If the benefit tier on the claim matches benefits.xlsx and the payer still denies: file a Level 1 appeal per Section 11.2.  
PR-1 / PR-2 / PR-3 | Deductible / Coinsurance / Copay | Read the patient responsibility amount directly from the ERA line item for this denial. Write that amount to claim.xlsx col Patient_Responsibility. Generate and send patient statement per Section 10.4.  
OA-23 | Charge exceeds fee schedule | Compare Paid_Amount to contracted rate. If underpaid: post to #billing-mgmt per Section 12.  
PI-204 | Not medically necessary | Gather PA approval, LMN, clinical notes, IgG labs from . File Level 1 appeal per Section 11.2.  
  
## 11.2 Appeal Submission

  35. Gather from : original claim PDF, PA approval, physician LMN, visit_note export, and ERA/EOB showing the denial.

  36. Complete appeal_template.docx. Save as appeal_L[1 or 2]_[DOS].pdf.

  37. Email appeal to payer_rules.xlsx col Appeal_Submission_Email. Subject: [APPEAL L[1/2]] CareIG | [Patient Last Name] | MemberID: [Member_ID] | DOS: [DOS] | Claim: [Submission_Ref_Number] | CARC: [code]. Attach all documents.

  38. Update appeals/appeals_log.xlsx: DOS, CARC_Code, Appeal_Level, Appeal_Submitted_Date, Appeal_Status = Submitted.



  39. Post to #billing-appeals: [APPEAL FILED L[1/2]] [CASE_ID] | DOS | Payer | CARC.



Follow-up: if (today − Appeal_Submitted_Date) ≥ 15 days and Appeal_Status = Submitted, call payer appeal department. Log in col Followup_Log: [Date] [Time] | Rep: [name] | Ref#: [#] | Next: [date].

If Level 2 denied: post to #billing-mgmt: [L2 DENIED] CASE_ID. Director of Revenue Cycle determines next action (write-off, IRO request, or state commissioner complaint).

Log to audit_log.xlsx: Action = Appeal Submitted.

# 12\. Escalation & Monitoring

## 12.1 Escalation Paths

Scenario | Slack Channel | Action  
---|---|---  
PA pending > 5 days | #intake-mgmt | Post: [PA DELAY] CASE_ID | Payer | Days Pending. Supervisor follows up with payer.  
Claim unpaid, no ERA | #billing | Post: [AR FOLLOWUP] CASE_ID | [days] outstanding | [Payer]. Log payer call in claim.xlsx col AR_Followup_Log.  
Payer underpaid vs contract | #billing-mgmt | Post: [UNDERPAYMENT] CASE_ID | Expected: $[rate] | Received: $[paid]. Director or contracting team reviews contract terms.  
Patient balance >$500, unresolved | #billing-mgmt | Confirm 3 contact attempts in intake.xlsx. If <3: email patient. If 3+: post to #billing-mgmt requesting collections authorization from Director.  
Write-off request >$200 | #billing-mgmt | Post: [WRITE-OFF REQUEST] CASE_ID | Amount: $[amount] | Reason: [reason]. Requires Director approval before actioning.  
Level 2 appeal denied | #billing-mgmt | Post: [L2 DENIED] CASE_ID. Director determines: write-off, IRO, or state complaint.  
Legal threat or attorney communication | #compliance | STOP. Do not respond or modify case files. Post: [LEGAL THREAT] CASE_ID. Director of Operations and legal@careig.com must be notified immediately.  
Suspected fraud or billing abuse | #compliance | STOP. Do not discuss elsewhere or modify files. Post: [COMPLIANCE REPORT] CASE_ID. Call Compliance Hotline.  
Wrong drug lot/dose from partner pharmacy | #clinical-scheduling | Do not administer. Document in clinical.xlsx col Drug_Issue_Notes. Post: [DRUG ISSUE] CASE_ID — visit on hold. Contact partner pharmacy.  
  
## 12.2 Workflow Monitoring

The intake supervisor, billing supervisor, or designated lead is responsible for reviewing open cases each morning. For each active case, check the condition in the left column against the relevant file. If the condition is true and the Slack message has not yet been sent, send it now. Do not wait for the assigned staff member to flag it — this review is a supervisory responsibility.

Condition | Slack Notification  
---|---  
audit_log.xlsx has Referral Received for CASE_ID but no BVS Assigned entry | #intake-alerts: [UNASSIGNED] CASE_ID — no BVS assigned.  
benefits.xlsx col BV_Complete is blank after BVS Assigned log entry | #intake-alerts: [BV OVERDUE] CASE_ID.  
auth.xlsx col PA_Submission_Date is blank after BV_Complete = YES | #intake-alerts: [PA NOT SUBMITTED] CASE_ID.  
auth.xlsx col PA_Status = Pending AND Last_Followup_Date is 2+ days old | Call payer. Update PA_Call_Log and Last_Followup_Date in auth.xlsx.  
clinical.xlsx col Handoff_Status is blank after auth.xlsx col PA_Status = Approved | #clinical-scheduling: [HANDOFF MISSING] CASE_ID.  
clinical.xlsx col Visit_Date is blank after Handoff_Status = Received | #clinical-scheduling: [UNSCHEDULED] CASE_ID.  
visit_note.xlsx col Nurse_Signature is blank after Visit_Date is populated | #clinical-scheduling: [UNSIGNED NOTE] CASE_ID.  
claim.xlsx col Submission_Date is blank after Nurse_Signature is populated | #billing: [CLAIM NOT SUBMITTED] CASE_ID.  
claim.xlsx col ERA_Received_Date is populated AND Payment_Posted_Date is blank | #billing: [ERA UNPOSTED] CASE_ID.  
A file in has Appeal_Submitted = blank | #billing-appeals: [DENIAL UNWORKED] CASE_ID.  
(today − claim.xlsx col DOS) in days exceeds 80% of payer_rules.xlsx col Timely_Filing_Days AND claim.xlsx col Submission_Date is blank | #billing: [TIMELY FILING RISK] CASE_ID | [days elapsed] of [limit] days | [Payer]. Submit claim immediately.  
  
# 13\. Reference Tables

## 13.1 HCPCS / J-Code Reference

Source: jcodes.xlsx. Always use visit_note.xlsx col Dose_Administered_Grams — never the ordered dose. Billed rates for each code are stored in fee_schedule.xlsx col Billed_Rate. To calculate Total_Billed for a claim: multiply each code's units by its Billed_Rate and sum all lines. Write the result to claim.xlsx col Total_Billed.

HCPC S | Description | Unit | Formula  
---|---|---|---  
J1459 | IVIG — Privigen, Gammagard (IV) | 500 mg | (g × 1000) ÷ 500  
J1557 | IVIG — Gammaplex (IV) | 500 mg | (g × 1000) ÷ 500  
J1559 | IVIG — Hizentra (SQ) | 100 mg | (g × 1000) ÷ 100  
J1560 | IVIG — Octagam (IV) | 500 mg | (g × 1000) ÷ 500  
J1561 | IVIG — Gamunex-C (IV or SQ) | 500 mg | (g × 1000) ÷ 500  
J1569 | IVIG — Gammagard Liquid (IV) | 500 mg | (g × 1000) ÷ 500  
J1575 | IVIG — HyQvia (SQ) | 100 mg | (g × 1000) ÷ 100  
J7030 | Normal Saline 0.9%, per 500 mL bag | 500 mL | Units = NS_500mL_Bags_Used  
J7050 | Normal Saline 0.9%, per 250 mL bag | 250 mL | Units = NS_250mL_Bags_Used  
J0171 | Diphenhydramine (Benadryl), per 50 mg | 50 mg | Units = mg administered ÷ 50. Requires documentation in Premeds_Administered.  
J2550 | Promethazine injection, per 25 mg | 25 mg | Units = mg administered ÷ 25. Same documentation rule as J0171.  
A4221 | IV infusion supplies, per visit | Per visit | Bill 1 unit per visit regardless of whether a pump is used.  
A4222 | Infusion pump supplies, per visit | Per visit | Bill 1 additional unit per visit when Pump_Used = YES. Bill alongside A4221, not instead of it.  
99600 | Home infusion nursing — first hour | Per visit | 1 unit. Default for non-Medicare.  
99603 | Home infusion nursing — each add'l hour | Per add'l hour | floor((Visit_Duration_Minutes − 60) ÷ 60) units.  
G0153 | Skilled nursing, home infusion (Medicare) | Per visit | 1 unit. Medicare Part B only. Replaces 99600/99603.  
T1029 | Nursing assessment, per visit | Per visit | Use when Nursing_Code_Pref = T1029. Verify by state.  
T1032 | Nursing visit, per diem | Per diem | Use when Nursing_Code_Pref = T1032. Verify by state.  
  
## 13.2 Unit Calculation Examples

Scenario | Result  
---|---  
30g Gammaplex 5% IV → J1557 | 30 × 1000 ÷ 500 = 60 units  
40g Privigen 10% IV → J1459 | 40 × 1000 ÷ 500 = 80 units  
6g Hizentra 20% SQ → J1559 | 6 × 1000 ÷ 100 = 60 units  
10g HyQvia 10% SQ → J1575 | 10 × 1000 ÷ 100 = 100 units  
Partial: ordered 30g, administered 20g → J1557 | Use 20g only: 20 × 1000 ÷ 500 = 40 units. Note in claim.xlsx col Partial_Infusion_Note.  
270-minute visit, non-Medicare | 99600 × 1 + 99603 × floor((270−60)÷60) = 99600 × 1 + 99603 × 3  
270-minute visit, Medicare Part B | G0153 × 1 only  
  
## 13.3 Drug Reference

Drug | Route | J-Code | Units/g | Notes  
---|---|---|---|---  
Gammaplex 5% / 10% | IV | J1557 | 2 | Diluent: 10% Dextrose — do NOT use NS. Refrigerate until 1 hr before use. Document bags used in visit_note.xlsx col Dextrose_500mL_Bags_Used. Bill via A4221 — do not bill J7030 or J7050.  
Octagam 5% / 10% | IV | J1560 | 2 | Do NOT shake. Confirm MD-ordered rate for 10%.  
Gammagard S/D | IV | J1459 | 2 | Reconstitute per package insert. Latex-free.  
Gammagard Liquid 10% | IV | J1569 | 2 | Off-label SQ use requires a separate MD order in .  
Privigen 10% | IV | J1459 | 2 | Contraindicated in hyperprolinemia. Check intake.xlsx col Contraindications.  
Gamunex-C 10% | IV or SQ | J1561 | 2 | Document route in visit_note.xlsx. Same J-code for both routes.  
Hizentra 20% | SQ | J1559 | 10 | Document self-infusion training on first visit in Education_Provided.  
HyQvia 10% | SQ | J1575 | 10 | Check payer_rules.xlsx for hyaluronidase co-billing requirement.  
  
_Reference the Drug column of this table whenever entering Drug_Name in files._

## 13.4 ICD-10 Reference

ICD-10 codes come from intake.xlsx col Diagnosis_ICD10. Confirm the code is in this table as written here and the required documentation exists in the case folder before submitting any PA or claim.

ICD-10 | Diagnosis | Required Documentation in  
---|---|---  
D83.9 | CVID, unspecified | MD progress note; IgG < 400 mg/dL collected within last 6 months preceding PA or claim (specimen collection date governs, not the lab report date).  
D80.0 | Hereditary hypogammaglobulinemia | MD note with hereditary basis; IgG level  
D80.1 | Nonfamilial hypogammaglobulinemia | IgG < 400 mg/dL lab result; MD progress note  
D80.6 | Antibody deficiency w/ near-normal Ig | Clinical notes; specialist consult preferred  
D89.3 | Immune reconstitution syndrome | Transplant documentation; oncology/hematology consult  
G61.0 | Guillain-Barré Syndrome | Neurology consult; NCS/EMG results; MD LMN  
ICD-10 | Diagnosis | Required Documentation in  
---|---|---  
G70.00 | Myasthenia gravis, without exacerbation | EMG/NCS; neurology note  
G70.01 | Myasthenia gravis, with exacerbation | Crisis history; set auth.xlsx col Urgency = STAT  
D69.3 | Immune thrombocytopenic purpura | Platelet count labs; MD diagnosis note  
B20 | HIV disease | CD4 count; viral load; HIV diagnosis; MD LMN  
Z94.0–Z94.9 | Transplant status | Transplant surgical record or discharge summary  
  
## 13.5 Payer Guidelines

Payer Type | Claim Format | Key Rules  
---|---|---  
Medicare Part B | Email (PDF) | Use G0153 for nursing. Apply MSP rules. Verify MAC in payer_rules.xlsx.  
Medicare Advantage | Email (PDF) per plan | Confirm IVIG benefit placement (medical vs pharmacy) in benefits.xlsx col Benefit_Type.  
Medicaid | Email (PDF) per state | PA required in most states. Check formulary and nursing code per state in payer_rules.xlsx.  
Commercial PPO | Email (PDF) | Confirm CareIG_Network_Status = In-Network before scheduling.  
Commercial HMO | Email (PDF) | PCP referral may be required. Document in benefits.xlsx col Referral_Required.  
Accredo / Coram (OON) | CareIG bills nursing only | Do NOT bill drug J-code. Bill: 99600/99603, A4221/A4222, pre-med J-codes, saline only.  
  
# 14\. Appendix A — Scripts & Templates

## Template 1: Unable to Reach Patient — Email to Referring Physician
    
    
    Recipient: [intake.xlsx col Physician_Email]
    Subject line: Unable to Contact Patient  |  CASE_ID: [CASE_ID]
    
    
    
    Body:
    “Dear Dr. [Physician_Name],
    
    
    
    We received a referral for [Patient First Last] (DOB: [MMDDYYYY]).
    After 3 contact attempts, we have been unable to reach the patient
    at the number on file: [Patient_Phone].
    
    
    
    Attempt 1: [intake.xlsx Contact_Attempt_Log entry 1]
    Attempt 2: [intake.xlsx Contact_Attempt_Log entry 2]
    Attempt 3: [intake.xlsx Contact_Attempt_Log entry 3]
    
    
    
    Please provide an alternate contact or assist in connecting the patient
    with our team. We cannot proceed until contact is established.
    
    
    
    [Patient Rep Full Name] — CareIG Specialty Pharmacy, Intake”
    

## Template 2: Peer-to-Peer Request Email to Physician
    
    
    DATE: [today]
    TO:   Dr. [Physician_Name]  |  EMAIL: [intake.xlsx col Physician_Email]
    FROM: CareIG Specialty Pharmacy — Prior Authorization
    RE:   P2P Review Request  |  CASE_ID: [CASE_ID]
          Patient: [First Last]  |  DOB: [Patient_DOB]
    
    
    
    Dear Dr. [Physician_Name],
    [Patient_Last_Name]'s PA for [auth.xlsx PA_Drug_Submitted] [PA_Dose_Submitted]g was
    denied by [Payer] with reason: [auth.xlsx PA_Denial_Reason].
    The payer has offered a peer-to-peer review. Available slots:
    [auth.xlsx P2P_Available_Slots — one per line]
    
    
    
    To schedule: call [benefits.xlsx PA_Phone]
    
    
    
    No response within 2 business days = CareIG will file a Level 1 written appeal.
    Reply to: pa@careig.com
    
    
    
    [BVS Name] — CareIG Specialty Pharmacy, Prior Authorization
    

## Template 3: Appeal Letter — Level 1 and Level 2
    
    
    DATE: [today]
    TO:   [Payer] Appeals Dept.
          [payer_rules.xlsx col Appeal_Submission_Email]
    FROM: CareIG Specialty Pharmacy  |  NPI: [CareIG_NPI]  |  Tax ID: [CareIG_Tax_ID]
    
    
    
    APPEAL LEVEL: [1 / 2]
    Patient:      [Last Name, First Name]
    Member ID:    [intake.xlsx Primary_Member_ID]
    DOS:          [claim.xlsx DOS]
    Claim #:      [claim.xlsx Submission_Ref_Number]
    CARC:         [code] — [description]
    Billed:       $[claim.xlsx Total_Billed]
    
    
    
    Dear Appeals Department,
    
    
    
    CareIG Specialty Pharmacy submits this Level [1/2] appeal for [Patient Name].
    The claim was denied with CARC [code]: [description].
    
    
    
    Basis for Appeal:
    
    
    
    PA #[auth.xlsx PA_Number] was approved for [PA_Approved_Drug] [PA_Approved_Dose]g,
    effective [PA_Effective_Date] through [PA_Expiration_Date]. The service on [DOS] is
    consistent with the approved authorization and ICD-10 [Diagnosis_ICD10].
    [Add specific clinical basis referencing attached documents.]
    
    
    
    Attached:
    

`1. Original claim — claim_[DOS].pdf`

`2. PA approval — pa_approval_[Payer].pdf (PA#: [PA_Number])`

`3. Physician LMN — lmn_[PhysicianName].pdf`

`4. Nursing visit note (exported from visit_note.xlsx)`

`5. Lab results — igglevel_[MMDDYYYY].pdf`

`6. ERA/EOB — era_[DOS]_[Payer].pdf`
    
    
    CareIG requests reconsideration at contracted rate: $[payer_rules.xlsx
    Contracted_Rate].
    Contact: billing@careig.com  |  [CareIG Billing Phone]
    
    
    
    [Billing Specialist Name, Credential] — CareIG Specialty Pharmacy, Billing
    

**— END OF DOCUMENT — CareIG-SOP-BILL-001 v5.0 —**

-- DSC 650 Final Project
-- Hive managed table for the Loan Approval Prediction dataset

CREATE TABLE loan_approval (
  loan_id STRING,
  gender STRING,
  married STRING,
  dependents STRING,
  education STRING,
  self_employed STRING,
  applicant_income INT,
  coapplicant_income DOUBLE,
  loan_amount DOUBLE,
  loan_amount_term DOUBLE,
  credit_history DOUBLE,
  property_area STRING,
  loan_status STRING
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
TBLPROPERTIES ("skip.header.line.count"="1");

LOAD DATA INPATH '/data/loan_approval/loan_approval.csv'
INTO TABLE loan_approval;

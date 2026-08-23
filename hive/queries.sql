-- DSC 650 Final Project
-- Representative Hive queries for the Loan Approval Prediction dataset

-- Verify that the managed Hive table was successfully populated.
-- Result: 614 records.
SELECT COUNT(*) AS total_records
FROM loan_approval;

-- Aggregate loan applications by approval status to verify
-- the loan_status field and demonstrate Hive aggregation.
SELECT loan_status, COUNT(*) AS application_count
FROM loan_approval
GROUP BY loan_status;

-- Display sample records to validate that the dataset columns
-- align correctly with the Hive table schema.
SELECT *
FROM loan_approval
LIMIT 5;

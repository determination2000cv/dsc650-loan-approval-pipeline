"""
DSC 650 Final Project
Loan Approval Prediction - Spark Data Processing

This supporting script demonstrates the preprocessing used for the
Loan Approval Prediction dataset before machine learning. The complete
ML workflow, model evaluation, and HBase write are implemented in analysis.py.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
from pyspark.ml.feature import VectorAssembler


def main():
    spark = (
        SparkSession.builder
        .appName("LoanApprovalProcessing")
        .enableHiveSupport()
        .getOrCreate()
    )

    # Read the managed Hive table created from the HDFS dataset.
    loan_df = spark.sql("""
        SELECT
            applicant_income,
            coapplicant_income,
            loan_amount,
            loan_amount_term,
            credit_history,
            loan_status
        FROM loan_approval
    """)

    # Convert the Y/N loan outcome into a numeric ML label.
    loan_df = loan_df.withColumn(
        "label",
        when(col("loan_status") == "Y", 1.0).otherwise(0.0)
    )

    feature_cols = [
        "applicant_income",
        "coapplicant_income",
        "loan_amount",
        "loan_amount_term",
        "credit_history"
    ]

    # Remove records with missing values in fields used by the model.
    ml_df = loan_df.select(*(feature_cols + ["label"])).na.drop()

    # Assemble numeric predictors into the feature vector expected by MLlib.
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features"
    )

    processed_df = assembler.transform(ml_df).select("features", "label")

    print("Original Hive rows:", loan_df.count())
    print("Rows available after preprocessing:", processed_df.count())

    spark.stop()


if __name__ == "__main__":
    main()

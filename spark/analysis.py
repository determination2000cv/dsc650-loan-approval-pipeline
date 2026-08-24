from pyspark.sql import SparkSession
from pyspark.sql.functions import when, col
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import (
    MulticlassClassificationEvaluator,
    BinaryClassificationEvaluator
)
import happybase

# Start Spark with Hive support
spark = (
    SparkSession.builder
    .appName("LoanApprovalML")
    .enableHiveSupport()
    .getOrCreate()
)

print("=== Loading data from Hive ===")

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

print("Hive row count:", loan_df.count())

# Convert Y/N loan status to a numeric label
loan_df = loan_df.withColumn(
    "label",
    when(col("loan_status") == "Y", 1.0).otherwise(0.0)
)

# Numeric predictor columns used by the model
feature_cols = [
    "applicant_income",
    "coapplicant_income",
    "loan_amount",
    "loan_amount_term",
    "credit_history"
]

# Remove rows with missing values in the ML fields
ml_df = loan_df.select(*(feature_cols + ["label"])).na.drop()

print("Rows available for ML:", ml_df.count())

# Assemble predictor columns into a feature vector
assembler = VectorAssembler(
    inputCols=feature_cols,
    outputCol="features"
)

assembled_df = assembler.transform(ml_df).select("features", "label")

# Split into training and testing datasets
train_data, test_data = assembled_df.randomSplit([0.70, 0.30], seed=42)

print("Training rows:", train_data.count())
print("Testing rows:", test_data.count())

# Train Logistic Regression model
lr = LogisticRegression(
    featuresCol="features",
    labelCol="label",
    maxIter=50
)

model = lr.fit(train_data)

print("=== Logistic Regression training completed ===")

# Generate predictions
predictions = model.transform(test_data)

# Evaluate model
accuracy = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="accuracy"
).evaluate(predictions)

precision = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedPrecision"
).evaluate(predictions)

recall = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="weightedRecall"
).evaluate(predictions)

f1 = MulticlassClassificationEvaluator(
    labelCol="label",
    predictionCol="prediction",
    metricName="f1"
).evaluate(predictions)

auc = BinaryClassificationEvaluator(
    labelCol="label",
    rawPredictionCol="rawPrediction",
    metricName="areaUnderROC"
).evaluate(predictions)

print("=== Model Evaluation Metrics ===")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"AUC:       {auc:.4f}")

# Write model metrics into HBase
print("=== Writing metrics to HBase ===")

connection = happybase.Connection("master")
connection.open()

table = connection.table("loan_model_metrics")

table.put(
    b"logistic_regression_run1",
    {
        b"metrics:accuracy": str(accuracy).encode(),
        b"metrics:precision": str(precision).encode(),
        b"metrics:recall": str(recall).encode(),
        b"metrics:f1": str(f1).encode(),
        b"metrics:auc": str(auc).encode()
    }
)

connection.close()

print("Model metrics successfully written to HBase.")
print("=== Spark ML pipeline completed successfully ===")

spark.stop()

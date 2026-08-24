# Architecture

The project architecture follows the required DSC 650 end-to-end pipeline:

**Source Data → Apache NiFi → HDFS → Apache Hive → Apache Spark MLlib → Apache HBase**

Spark workloads are submitted and managed through **YARN**.

The architecture diagram is stored at:

[`architecture-diagram.png`](architecture-diagram.png)

The diagram provides a high-level view of the Loan Approval Prediction pipeline, including the HDFS storage path, Hive managed table, Spark MLlib processing, YARN execution, and HBase metrics persistence.

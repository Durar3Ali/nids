# High-Performance Binary Network Intrusion Detection System (NIDS)

This repository contains a production-grade machine learning system optimized for real-time binary classification of network anomalies using the UNSW-NB15 dataset framework. The core engineering objective is the optimization of detection sensitivity to reduce critical False Negatives while ensuring the model remains computationally efficient enough for integration into high-throughput network routing layers.

A lightweight interactive frontend application has been developed alongside the pipeline as a demonstration interface to showcase the operational NIDS.

---

## Repository Structure

```text
nids/
│
├── models/
│   ├── optimized_lightgbm.txt   # Native LightGBM configuration file (engine-agnostic)
│   └── scaler.joblib            # Serialized Scikit-Learn standardizer matrix
│
│
├── app.py                       # Demonstration interface code
├── requirements.txt             # Platform-agnostic execution dependencies
└── README.md                    # System documentation and analysis
```

---

## Engineering Pipeline & Technical Analysis

### 1. Data Pipeline & Feature Engineering
The upstream processing layers handle significant class imbalances inherent to raw security logging metrics, where standard traffic data dwarfs attack occurrences by several orders of magnitude.

* **Categorical Transformation:** High-cardinality nominal values across `proto`, `service`, and `state` attributes are parsed and vectorized into an aligned one-hot encoded matrix.
* **Feature Standardization:** Volumetric features exhibiting high variance (such as source/destination bytes and packet transmission rates) are scaled via empirical mean and variance shifts to prevent gradient descent bias during training.
* **Loss Function Constraint:** Initial classification experiments embedded structural weight adjustments (`class_weight="balanced"`) directly into baseline algorithmic steps to prevent optimization bias toward the majority class.

### 2. Algorithmic Optimization & Error Diagnostics
During the Phase 2 modeling stage, baseline models (Logistic Regression and Random Forest) were evaluated against a Gradient Boosted Decision Tree framework (LightGBM). A systematic error diagnostic was executed specifically targeting False Negatives—malicious operations misclassified as benign network traffic.

```text
ERROR ANALYSIS DIAGNOSTIC METRIC EXTRACTION
------------------------------------------------------
Feature Group                        | Scaled Mean
------------------------------------------------------
Anomalous Feature 2 (dur)            | -0.112617
Anomalous Feature 4 (sbytes)         | -0.100780
------------------------------------------------------
```

* **The Analytical Insight:** Statistical profiling of the False Negative partition showed that missed attacks consistently displayed below-average connection durations and compressed payload sizes. Standard configurations misclassified these stealthy signatures (such as quick command injections or single-packet reconnaissance probes) as routine background network traffic.
* **The Optimization Loop:** To retune decision boundaries around low-volume anomalies, a structured hyperparameter search was completed using Stratified 3-Fold Cross-Validation. Tree morphology was restricted, and classification boundaries were sharpened using targeted parameter values:
  * `max_depth`: Enforced shallow split structures to prevent overfitting on deep structural noise.
  * `num_leaves`: Constrained the terminal node counts to enforce generalized, lower-complexity boundaries.
  * `scale_pos_weight`: Scaled the loss penalty multiplier on the attack class to prioritize anomalous detection patterns.

---

## Performance Evaluation

Following structural optimization, the fine-tuned framework was executed once against an independent, untouched testing dataset to establish authentic out-of-sample operational benchmarks.

### Out-of-Sample Confusion Matrix
```text
[[ 16301   2317]  --> [True Negative,  False Positive]
 [     1  23868]] --> [False Negative, True Positive]
```

### Operational Statistics
* **Area Under the ROC Curve (ROC-AUC):** 0.9893 (Confirming robust separation behavior under high feature variance).
* **Detection Recall (Class 1):** 99.99% (Reducing the critical system bypass rate down to 1 single missed intrusion instance out of 23,869 actual test samples).
* **Architectural Trade-Off Assessment:** Optimizing boundaries to register stealthy, low-volume anomalies generated an increase in false alarms (2,317 False Positives). In production network administration, minimizing False Negatives is prioritized over minimizing False Positives; reviewing a false alarm is computationally and operationally manageable, whereas failing to detect an active system breach introduces systemic security risks.

---

## Deployment & Production Notes

* **Engine-Agnostic Serialization:** The model is saved utilizing LightGBM's native text format (`optimized_lightgbm.txt`). This removes dependency serialization vulnerabilities associated with standard Python serialization formats (such as pickle) and enables high-speed integration into lower-level application runtimes like C++ or Go.
* **Data Drift Management:** Deploying this system into production network architectures requires continuous covariate shift tracking. Significant modifications in packet size baselines or network topology protocols will reduce model efficacy over time, necessitating automated diagnostic alerts to trigger offline data collection and retraining runs.

---

## Local Initialization

1. Clone the repository structure locally:
   ```bash
   git clone https://github.com
   cd nids-classifier
   ```

2. Standardize local execution environments:
   ```bash
   pip install -r requirements.txt
   ```

3. Launch the local validation interface demonstration:
   ```bash
   streamlit run app.py
   ```

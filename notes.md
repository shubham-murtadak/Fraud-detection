# Fraud Detection in Data Science: Revision Notes

## 1. What is Fraud Detection?
Fraud detection is the proactive identification of illicit activities within a business's operations. In the context of **Data Science and Machine Learning**, it is treated as an **Anomaly Detection** or **Binary Classification** problem. 

Because fraudulent transactions make up a tiny fraction of total business volume (often < 1%), standard machine learning models struggle to identify them. Data Scientists must use specialized techniques like:
- **Resampling techniques** (SMOTE, undersampling the majority class)
- **Algorithm choices** (LightGBM/XGBoost with aggressive `scale_pos_weight`, Isolation Forests)
- **Business-specific Feature Engineering** (e.g., velocity rules: "How many times was this IP address used in the last hour?")
- **Custom Evaluation Metrics** (Using PR-AUC and F1-Score instead of Accuracy).

---

## 2. Types of Financial Fraud
Based on the core vectors of attack, fraud generally falls into four main categories:

### A. Transaction Fraud
- **Description:** Unauthorized card usage.
- **How it works:** A bad actor steals credit/debit card numbers (via skimming or data breaches) and attempts to make unauthorized purchases online (Card-Not-Present) or physically.
- **Data Science Signal:** Anomalies in transaction amounts (testing micro-transactions or maxing out limits), rapid successive purchases, or mismatches between billing and shipping addresses.

### B. Identity Theft
- **Description:** Fake KYC (Know Your Customer) / stolen credentials.
- **How it works:** Fraudsters use stolen personal information (Social Security Numbers, IDs) or synthesize fake identities (Synthetic Identity Fraud) to open new accounts.
- **Data Science Signal:** Mismatches in credit bureau data, impossible combinations of SSN/DOB, or highly correlated but slightly altered PII (Personally Identifiable Information) across multiple applications.

### C. Account Takeover (ATO)
- **Description:** Hacker gains access and drains funds.
- **How it works:** Bad actors use phishing, malware, or credential stuffing (using passwords leaked from other sites) to log into a legitimate user's existing bank account.
- **Data Science Signal:** Sudden changes in IP address, device fingerprints (new OS/Browser), or behavioral biometrics (typing speed/mouse movements) that don't match the historical user profile.

### D. Loan / Credit Fraud
- **Description:** Fake profiles taking loans and disappearing.
- **How it works:** Scammers apply for personal loans, auto loans, or credit lines with no intention of ever paying them back (also known as "bust-out fraud").
- **Data Science Signal:** Unusual spikes in credit utilization, rapid accumulation of credit lines across multiple banks, or employment data that cannot be verified.

---

## 3. Why is it hard?
- **Extreme Class Imbalance:** Finding the 1 fraudster among 10,000 legitimate users.
- **Concept Drift:** Fraudsters actively adapt. Once you deploy a model that catches their specific attack, they will change their behavior the very next day. Models must be continuously retrained.
- **Cost of False Positives:** If a bank's model is too aggressive, it will decline legitimate transactions. This angers customers (friction) and causes reputational damage. Balancing precision and recall is critical.

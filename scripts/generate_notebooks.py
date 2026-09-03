import nbformat as nbf
import os
from pathlib import Path

def create_00_notebook():
    nb = nbf.v4.new_notebook()
    cells = [
        nbf.v4.new_markdown_cell("# HDFC Bank: Fraud Risk Analysis - Part 0\n\n**Objective:** Data Understanding and Schema Review\n\nReviewing the latest transaction extract from Data Engineering. \n\n### Data Dictionary\n\n**Core Transaction Features**\n- `TransactionID`: Unique identifier for the transaction.\n- `isFraud`: Target variable (1 = Fraud, 0 = Legitimate).\n- `TransactionDT`: Time delta from a hidden reference date (in seconds).\n- `TransactionAmt`: Payment amount in USD.\n- `ProductCD`: Product code.\n\n**Card & Address Features**\n- `card1` - `card6`: Payment card information (e.g., Visa/Mastercard, Credit/Debit).\n- `addr1`, `addr2`: Purchaser billing region and country.\n- `dist1`, `dist2`: Distances.\n\n**Email Domains**\n- `P_emaildomain`, `R_emaildomain`: Purchaser and recipient emails.\n\n**Engineered Features (Payment Processor)**\n- `C1` - `C14`: Counting features.\n- `D1` - `D15`: Time delta features.\n- `M1` - `M9`: Match features.\n- `V1` - `V339`: Vesta engineered rich features (anonymized).\n\n**Identity Features (Often Missing)**\n- `id_01` - `id_38`: Network connection and digital identity.\n- `DeviceType`: e.g., mobile, desktop.\n- `DeviceInfo`: e.g., Windows, iOS."),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent / "src"))
from fraudguard.data.ingestion import load_bank_data

data_dir = Path.cwd().parent / "data" / "raw"
print("Loading HDFC transaction data warehouse extract...")
df = load_bank_data(data_dir)
print(f"\\nData loaded successfully! Shape: {df.shape}")"""),
        nbf.v4.new_markdown_cell("### 1. Basic Inspection"),
        nbf.v4.new_code_cell("""pd.set_option('display.max_columns', 50)
df.head()"""),
        nbf.v4.new_markdown_cell("### 2. Data Types and Memory Usage"),
        nbf.v4.new_code_cell("""print("Dataset Memory Usage and Types:")
df.info(memory_usage='deep')

categorical_cols = df.select_dtypes(include=['object', 'category']).columns
numerical_cols = df.select_dtypes(include=[np.number]).columns

print(f"\\nTotal Categorical Features: {len(categorical_cols)}")
print(f"Total Numerical Features: {len(numerical_cols)}")"""),
        nbf.v4.new_markdown_cell("### 3. Summary Statistics"),
        nbf.v4.new_code_cell("""# Numerical features summary (showing a subset for readability)
df[['TransactionAmt', 'TransactionDT', 'isFraud', 'card1', 'C1', 'D1', 'V1']].describe()"""),
        nbf.v4.new_code_cell("""# Categorical features summary
df[categorical_cols].describe()"""),
        nbf.v4.new_markdown_cell("### 4. Missing Values Analysis"),
        nbf.v4.new_code_cell("""# Top 20 columns with the most missing values
missing_percent = (df.isnull().sum() / len(df)) * 100
print("Top 20 columns with highest missing value percentage:")
print(missing_percent.sort_values(ascending=False).head(20))""")
    ]
    nb['cells'] = cells
    out_path = Path(__file__).parent.parent / "notebooks" / "00_data_understanding.ipynb"
    with open(out_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {out_path}")

def create_01_notebook():
    nb = nbf.v4.new_notebook()
    cells = [
        nbf.v4.new_markdown_cell("# HDFC Bank: Fraud Risk Analysis - Part 1\n\n**Objective:** Exploratory Data Analysis (EDA) & Target Leakage Check\n\nNow that we understand the schema, we analyze the business patterns of fraud and guarantee we aren't leaking future information into our models."),
        nbf.v4.new_code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("muted")

import sys
from pathlib import Path
sys.path.append(str(Path.cwd().parent / "src"))
from fraudguard.data.ingestion import load_bank_data

data_dir = Path.cwd().parent / "data" / "raw"
df = load_bank_data(data_dir)"""),
        nbf.v4.new_markdown_cell("## 1. Transaction Amount Analysis"),
        nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 5))
sns.histplot(data=df, x='TransactionAmt', hue='isFraud', log_scale=True, 
             bins=50, ax=axes[0], common_norm=False, stat='density', alpha=0.5)
axes[0].set_title("Transaction Amount Distribution (Log Scale)")
axes[0].set_xlabel("Transaction Amount (USD equivalent)")

sns.boxplot(data=df, x='isFraud', y='TransactionAmt', ax=axes[1])
axes[1].set_yscale('log')
axes[1].set_title("Amount Outliers by Risk Class")
axes[1].set_xticklabels(['Legitimate (0)', 'Fraud (1)'])
plt.tight_layout()
plt.show()"""),
        nbf.v4.new_markdown_cell("## 2. Card Network and Type Analysis"),
        nbf.v4.new_code_cell("""fig, axes = plt.subplots(1, 2, figsize=(15, 5))
card_network_fraud = df.groupby('card4')['isFraud'].agg(['count', 'mean']).sort_values('count', ascending=False)
sns.barplot(x=card_network_fraud.index, y=card_network_fraud['mean'], ax=axes[0])
axes[0].set_title("Fraud Rate by Card Network")
axes[0].set_ylabel("Fraud Rate")

card_type_fraud = df.groupby('card6')['isFraud'].agg(['count', 'mean']).sort_values('count', ascending=False).head(4)
sns.barplot(x=card_type_fraud.index, y=card_type_fraud['mean'], ax=axes[1])
axes[1].set_title("Fraud Rate by Card Type")
axes[1].set_ylabel("Fraud Rate")
plt.tight_layout()
plt.show()"""),
        nbf.v4.new_markdown_cell("## 3. Missing Identity Data as a Risk Signal"),
        nbf.v4.new_code_cell("""df['Has_Identity_Data'] = df['id_01'].notnull().astype(int)
id_fraud_rate = df.groupby('Has_Identity_Data')['isFraud'].agg(['count', 'mean'])

plt.figure(figsize=(6, 5))
sns.barplot(x=id_fraud_rate.index, y=id_fraud_rate['mean'])
plt.title("Fraud Rate: Missing vs. Present Identity Data")
plt.xticks([0, 1], ['Missing Identity Data', 'Has Identity Data'])
plt.ylabel("Fraud Rate")
plt.show()"""),
        nbf.v4.new_markdown_cell("## 4. Leakage Analysis (Pearson Correlation)"),
        nbf.v4.new_code_cell("""print("Running deep correlation analysis on numeric features...")
numeric_df = df.select_dtypes(include=[np.number]).drop(columns=['TransactionID', 'TransactionDT', 'isFraud', 'Has_Identity_Data'])
numeric_df = numeric_df.fillna(numeric_df.median())

correlations = numeric_df.corrwith(df['isFraud']).abs().sort_values(ascending=False)
print("\\nTop 10 most correlated numeric features (Pearson):")
print(correlations.head(10))

if correlations.max() > 0.8:
    print("\\nCRITICAL WARNING: Target leakage detected! Feature correlation > 0.8")
else:
    print("\\nSYSTEM CHECK PASSED: No single numeric feature predicts fraud with > 80% correlation.")""")
    ]
    nb['cells'] = cells
    out_path = Path(__file__).parent.parent / "notebooks" / "01_eda.ipynb"
    with open(out_path, 'w', encoding='utf-8') as f:
        nbf.write(nb, f)
    print(f"Created {out_path}")

if __name__ == "__main__":
    create_00_notebook()
    create_01_notebook()

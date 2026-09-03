import sys
import logging
from pathlib import Path
from fraudguard.data.ingestion import load_bank_data
from fraudguard.data.validation import validate_raw_data
import pandera as pa

# Set up simple console logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def main():
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data" / "raw"
    
    logger.info("=== Starting Data Ingestion ===")
    try:
        df = load_bank_data(data_dir)
    except FileNotFoundError as e:
        logger.error(f"Failed to load data: {e}")
        logger.error("Please ensure you have downloaded train_transaction.csv and train_identity.csv into data/raw/")
        sys.exit(1)
        
    logger.info("=== Starting Data Validation ===")
    try:
        validated_df = validate_raw_data(df)
        logger.info("✅ SUCCESS: Data passed schema validation!")
        
        # Print a simple data quality report
        logger.info("--- Data Quality Report ---")
        logger.info(f"Total Transactions: {len(validated_df):,}")
        logger.info(f"Fraud Rate: {validated_df['isFraud'].mean():.2%}")
        missing_identity = validated_df['id_01'].isna().mean() if 'id_01' in validated_df else 0.0
        logger.info(f"Transactions missing identity info: {missing_identity:.2%}")
        
    except pa.errors.SchemaError as e:
        logger.error("❌ FAILURE: Data failed schema validation!")
        logger.error(str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()

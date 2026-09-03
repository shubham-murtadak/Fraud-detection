import os
import subprocess
import sys
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    raw_dir = data_dir / "raw"
    
    # Create directories if they don't exist
    raw_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Ensuring Kaggle API is configured...")
    kaggle_json_path = Path.home() / ".kaggle" / "kaggle.json"
    if not kaggle_json_path.exists():
        print(f"Error: {kaggle_json_path} not found.")
        print("Please download your API key from Kaggle (kaggle.com -> Settings -> API -> Create New Token) and place it in ~/.kaggle/kaggle.json")
        print("For Windows, it should be in C:\\Users\\<YourUsername>\\.kaggle\\kaggle.json")
        sys.exit(1)
        
    print(f"Downloading IEEE-CIS Fraud Detection dataset to {raw_dir}...")
    try:
        # We assume kaggle CLI is installed in the current environment
        subprocess.run([
            "kaggle", "competitions", "download", 
            "-c", "ieee-fraud-detection", 
            "-p", str(raw_dir)
        ], check=True)
        print("Download complete.")
        
        # Unzip the downloaded file
        zip_path = raw_dir / "ieee-fraud-detection.zip"
        if zip_path.exists():
            print(f"Unzipping {zip_path}...")
            import zipfile
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(raw_dir)
            print("Extraction complete.")
            zip_path.unlink()
            print("Removed zip file.")
            
    except subprocess.CalledProcessError as e:
        print(f"Error during download: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: 'kaggle' command not found. Ensure it is installed in your virtual environment (e.g. run pip install kaggle).")
        sys.exit(1)

if __name__ == "__main__":
    main()

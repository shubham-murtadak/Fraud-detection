import nbformat as nbf
import json

path = r'd:\Gravitones\Fraud_detection\notebooks\07_advanced_ensembling.ipynb'
with open(path, 'r', encoding='utf-8') as f:
    nb = nbf.read(f, as_version=4)

for cell in nb.cells:
    if cell.cell_type == 'code' and "cv='prefit'" in cell.source:
        cell.source = cell.source.replace("cv='prefit'", "cv=2")
        cell.source = cell.source.replace("calibrated_ensemble.fit(X_test_processed, y_test)", "calibrated_ensemble.fit(X_train_processed, y_train)")

with open(path, 'w', encoding='utf-8') as f:
    nbf.write(nb, f)
print('Notebook patched successfully')

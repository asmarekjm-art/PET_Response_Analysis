from pathlib import Path
import subprocess
import sys

scripts = [
    "parser_pet.py",
    "classifier_diagnosis.py",
    "classifier_response.py",
    "classifier_details.py",
    "classifier_treatment.py",
    "merge_results.py"
]

for script in scripts:

    print()
    print("=" * 70)
    print(f"Uruchamianie: {script}")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, script]
    )

    if result.returncode != 0:
        print(f"\nBŁĄD W: {script}")
        break

print()
print("=" * 70)
print("PIPELINE ZAKOŃCZONY")
print("=" * 70)
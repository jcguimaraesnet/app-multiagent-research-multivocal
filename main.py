"""Entrypoint.

Steps 1-4 (per origin): python main.py --origin <scopus|google|github|hf> --step <1|2|3|4>
Step 5 (all origins):   python main.py --step 5   # export blind human-review .xlsx sheets
Step 8 (per origin):    python main.py --origin <origin> --step 8   # RQ2 form and activity
Steps 9-10 (all):       python main.py --step 9 | --step 10   # export / apply its review sheet
"""

from rmr.cli import main

if __name__ == "__main__":
    main()

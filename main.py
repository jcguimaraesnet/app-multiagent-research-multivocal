"""Entrypoint.

Steps 1-4 (per origin): python main.py --origin <scopus|google|github|hf> --step <1|2|3|4>
Step 5 (all origins):   python main.py --step 5   # export blind human-review .xlsx sheets
"""

from rmr.cli import main

if __name__ == "__main__":
    main()

Create a BNF lark grammar for the real test language.

Workflow:
1. Every file in the samples/ directory must pass the lark grammar validation test
2. Maintain a list of filenames and pass/fail state (in data.json), if it doesn't exist - scan samples/*.rts to build it assuming that no parsing tests succeed.  Always keep this data.json up to date, if there are new files in samples/ add them to data.json with a failed parsing state, if files in data.json don't exist in samples/ then remove the entry from the data.json
3. Find the first file in data.json that does not validate - making a note of all the files that DO validate properly
4. Adjust the lark grammar in the smallest way possible to fix the parsing/validation problem, and try parsing again - IMPORTANT: all files that parse must continue to parse - changes you make to parsing SHOULD NOT result in a parse regression error
5. When a file parses correctly update the data.json and move on to the next file

Validation:
- use the validate_rts.py script to test an .rts file against the lark grammar
- this can be run without args to test ALL files in the /samples/ directory or use --file to pick a specific .rts file
- when an .rts file passes using validate_rts.py, use the enchanged validator to run another test - this must also pass, if not, then the file being validated has a parse problem.

Rules:
1. DO NOT CHANGE ANYTHING IN THE /samples/ directory - ever
2. When testing / validating - a common error is that a rule consumes EVERYTHING after it - make sure this is never the case.
3. Use search to get the latest documentation or examples.
4. When fixing grammar, try changes that are not greedy first. 

Prerequisites:
1. Use the venv called 'realtestextract' for all python scripts - if it does not exist it can be set up via tools/setup_realtest_env.sh or via tools/setup_realtest_env.ps1
2. This venv is located at the root of the repository

Progress Log:
- 2025-10-10: Updated both validators with `--samples-dir`, generated `data.json` baseline (113/113 pass), no failing files currently identified for grammar fixes.

Detailed Plan:
1. Activate the realtestextract virtual environment from the repository root (`source realtestextract/bin/activate`) to guarantee a consistent Python toolchain.
2. Work from the bnf/ directory and leave bnf/samples/ untouched; treat those inputs strictly as read-only fixtures.
3. Generate or refresh bnf/data.json by scanning bnf/samples/*.rts, inserting any new filenames with status `"fail"` and pruning entries without a backing sample file.
4. Use the validation section rules above to establish the baseline pass/fail set and confirm bnf/data.json captures the results.
5. Re-run the validator with `--early` to capture detailed diagnostics for the first failing sample; stash the error context for targeted grammar fixes.
6. Iterate over failing samples in data.json order: inspect the offending snippet, cross-reference bnf/lark/realtest.lark and the latest extracted manual text (create it under versions/.../manual.txt first if missing), then apply the minimal grammar tweak needed to parse the construct without regressing earlier passes.
7. After each grammar adjustment, run both validator scripts to ensure section boundaries stay intact; flip the corresponding data.json entry to `"pass"` only when the sample succeeds.
8. Continue until validate_rts.py reports all PASS, then record the changes and open questions in bnf/AGENTS.md to inform downstream LLM-context packaging.

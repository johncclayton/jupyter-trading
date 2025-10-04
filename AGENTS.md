The goal is to extract features and documentation related to the Real Test Script language from the PDF manual, 
and make it available in a structured format for consumption by a large language model.

The BNF grammar for the Real Test Language is in the bnf/ directory - the grammar file is bnf/lark/realtest.lark, this might be useful when trying to produce code or understand existing code.

The plan/ directory contains the plans that describe the PDF extraction process, the exec/ are more detailed
tasks lists.

There is a python env called realtestextract - use that wherever possible.

The samples/ directory contains read-only sample .rts script files. 
The versions/ directory is where the versioned real test PDF manuals are stored and worked on.
The tools/ directory contains python code suitable for extracting from the PDF and working with the resulting text

Rules:
1. DO NOT CHANGE ANYTHING IN THE samples/ directory - ever
2. Only focus on the language aspects of Real Test, not on the UI 
3. Do not over engineer the solution - repeatable results are more important than perfection.
4. IMPORTANT: the manual MAY CONTAIN more than the BNF, meaning the BNF is just there to help/guide - it might be out of date when the process runs.

Refer to the plan/ directory for further detailed instructions, executed in numerical order and defined in greater detail in exec/ directory (the plan/ files map 1:1 to the exec/ directory).
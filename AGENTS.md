# Mission

The goal is to make it possible for LLMs to write perfect real test code. 

1. Extraction of a BNF grammar that can parse EVERYTHING in the samples/ directory, this is in the bnf/ directory
2. Extraction of the text from the Real Test Manual
3. Creation of a "LLM Context Pack" - which is a directory containing an AGENTS.MD file, and reference files extracted from step 2 above, containing at least:
 - list of functions, names, arguments, description of purpose (extracted from documentation)
 - lark (or other) grammar definition
 - program to validate RT code - perhaps even written as an MCP server so LLMs can test their code quickly

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
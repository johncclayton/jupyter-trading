# Plan 1: Extract and Understand RealTest Language

The goal is to extract as much information as possible about the real test script language into text files.

It's important to understand that some of the manual deals with the Real Test UI, and some of it with the Real Test
Script (.rts) language.  Focus on the script language - and not on the UI, unless the portions of the UI help provide
meaning and or context.

In the generated output, never use full path names - always use relative path names.  Where this might be a problem for further processing steps, make sure these steps resolve the relative path names properly.

All code goes into the tools/ directory.

Here are the general steps to extract:

1. **Prepare Versioned Artifacts**  
   - Input: Repository root containing at least one `RealTest*.pdf`, populated `samples/` with `.rts` examples.  
   - Actions: Identify newest matching PDF by timestamp; derive version name `YYYYMMDD-realtest-guide`; create `versions/<version>/`; move PDF to `versions/<version>/manual.pdf`; ensure `samples/` exists.  
   - Output: `versions/<version>/manual.pdf`, ready-to-use `samples/` directory.

2. **Run Standardized Text Extraction**  
   - Input: `versions/<version>/manual.pdf`.  
   - Actions: Write code to extract text from the input, and store the results in the output - call this code 2-standard-text-extraction.py
   - Output: `versions/<version>/manual.txt` (UTF-8 plain text).

3. **Build Manual Structure and Glossary**  
   - Input: `versions/<version>/manual.txt`.  
   - Actions: Write code to process the input, capture every heading and curated glossary terms into output called manual_structure.json
   - Output: `versions/<version>/manual_structure.json` (sections list + glossary array).

4. **Compile Function, Directive, and Statement Catalog**  
   - Input: `versions/<version>/manual.txt`, `samples/*.rts`.  
   - Actions: Extract all the language functions, descriptions and usage examples into a catalog called function_catalog.json
   - Output: `versions/<version>/function_catalog.json`.


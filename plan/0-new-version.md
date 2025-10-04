# Plan 0: Initialize Version Workspace

The goal is to create a fresh version directory for the RealTest manual before running any extraction steps.

1. **Discover Latest Manual Source**  
   - Input: Repository root containing `RealTest User Guide.pdf` (or matching `RealTest*.pdf`).  
   - Actions: Use `python -m tools.version_init` (dry-run mode) to locate the newest matching manual and confirm the planned source.  
   - Output: Resolved source manual path.

2. **Derive Version Identifier**  
   - Input: Source manual path.  
   - Actions: Allow the helper script to format today's date as `YYYYMMDD-realtest-guide`, ensuring the timestamp is recorded in UTC to avoid ambiguity.  
   - Output: Version string for directory naming.

3. **Create Version Directory**  
   - Input: Version string.  
   - Actions: Run `python -m tools.version_init` to create `versions/<version>/`; abort if the directory already exists to prevent accidental overwrites.  
   - Output: Empty `versions/<version>/` ready for artifacts.

4. **Copy Manual Into Version**  
   - Input: Source manual path, version directory.  
   - Actions: Let the helper script copy the manual to `versions/<version>/manual.pdf`; leave the original in place for reference.  
   - Output: Version-local manual ready for downstream tooling.

5. **Record Provenance**  
   - Input: Source manual path, version directory.  
   - Actions: Allow the helper script to write `versions/<version>/metadata.json` containing the source filename, UTC timestamp, and SHA256 of the copied PDF for reproducibility.  
   - Output: Metadata entry documenting the version creation.

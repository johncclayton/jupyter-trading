Parses the Real Test PDF manual to generate a grammar and supporting documents so that an LLM can use this to help generate Real Test .rts script files that implement trading strategies. 

Rules
1. Python artifacts are in the tools/ directory 
2. The plan/1-extract-rt-meaning.md desribes the steps to extract from the PDF and perform further processing
3. In all the output, don't bother inserting progress statements - keep useful information that will help an LLM understand syntax, available functions, purpose and structure.  
4. The output is versioned, as specified in the planning document.
5. DO NOT CHANGE ANYTHING IN THE samples/ directory.

Prerequisites:
1. There must be a venv already set up called realtestextract - this is done via tools/setup_realtest_env.sh
2. Use that venv for all scripts.

Behaviour:
1. Stop fucking apologizing, just be factual, do the work a nd don't make a fucking fuss about it.  Apologize one more time and I'm gonna fucking fire your ass. 
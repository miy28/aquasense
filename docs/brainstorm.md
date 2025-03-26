LLM aquasense attention mechanism

- pay attention to data trends 1 day at a time (attention_width = 1 day)
- current day response (predicted trends) = trends present in current attention window + response from previous day

- how to extract trends? ideas
    - clustering 
    - 'semantic' feature extraction via prompt engineering: tell the llm to look for certain behaviors
    - plot the data over time and feed it to llm (also prompt engineering)

- models/frameworks
    - llms: ollama, llama 3.2 small (1b) -> could run it locally
    - data analysis: tsfresh + scikit -> k-means, dbscan
    - rag: langchain

- feature engineering: real-time and offline. offline will probably run like once a day or something
- real-time features
    - derivative (slope) -> spikes are always a red flag, alert the user with an llm message

- offline features
    - just use tsfresh
# Privacy Manifesto 🛡️

At **Messenger Insights**, we believe that personal data analytics shouldn't come at the cost of privacy. Your conversations are private, and they should stay that way.

## Our Core Commitments

### 1. Zero Data Exfiltration
*   **Local Execution**: All Python code runs strictly on your local machine.
*   **No Servers**: We do not maintain any backend servers. There is no "cloud" component.
*   **No Telemetry**: We do not track usage, crash reports, or collect any metadata about your message history.

### 2. Open Source Transparency
*   **Auditable Code**: Our entire codebase is open source. You can inspect every line of `src/messenger_insights` to verify that no network requests are being made to external servers.
*   **Plotly JS**: The only external resource used is the standard [Plotly.js CDN](https://cdn.plot.ly/plotly-latest.min.js) for rendering graphs. If you prefer offline usage, you can download this script and point the template to a local copy.

### 3. Your Data, Your Storage
*   **Transient Processing**: Raw JSON data is streamed into memory for analysis and then discarded. 
*   **Local Caching**: We may create a local `.parquet` cache file in your output directory to speed up subsequent runs. This file remains on your disk and is never uploaded.
*   **Report Ownership**: The generated HTML report is a static file on your computer. You decide who sees it.

## Why This Matters
Many "social media analyzer" tools require you to upload your `.zip` backup to their servers. This is a massive security risk, exposing decades of private conversations, photos, and location data. 

**We built this tool to prove you can have powerful insights *without* the compromise.**

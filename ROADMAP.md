# 🗺️ Messenger Insights - Master Roadmap

## 🚀 The Vision
To build the **ultimate personal data observatory**.
We spend half our lives digital. This tool gives you a mirror to see who you are, how you communicate, and how your relationships evolve over time—without selling your data to advertisers.

---

## ✅ Completed (V1 & V2)

### Core Engine
- [x] **Streaming Parser**: `ijson` architecture to handle 10GB+ JSON files on low-RAM machines.
- [x] **Encoding Auto-Fix**: Solved Facebook's infamous "mojibake" (latin-1) encoding issue automatically.
- [x] **Platform Agnostic**:
    - [x] Facebook Messenger (JSON)
    - [x] Instagram DMs (JSON)
    - [x] WhatsApp (Text Logs)

### Analytics
- [x] **Response Time**: Accurate median minute-based response times (filtering sleep hours).
- [x] **Initiation Rate**: Who double texts? Who starts the conversation?
- [x] **Emoji DNA**: Frequency analysis of top emojis per person.
- [x] **Reaction Matrix**: Heatmap of specific reaction patterns (e.g. who "Loves" messages most).
- [x] **Verbosity**: Average message length comparison.

### Visual Polish ("Wrapped" Experience)
- [x] **Interactive Dashboard**: Client-side filtering (Date Range, Top N) with zero latency.
- [x] **Social Share Cards**: 9:16 aspect ratio cards for Instagram Stories.
- [x] **Charts**: Plotly.js powered Zoomable Timelines, Activity Heatmaps, and Bar Charts.
- [x] **Static Exports**: Generator for standalone PNG/HTML charts.

---

## 🔮 Phase 3: The "Smart" Era (LLMs & AI)
*The next frontier is not just counting words, but understanding meaning.*

- [ ] **"Chat with your History" (RAG)**
    - Integrate `langchain` and `Ollama`.
    - Allow users to query: *"What movies did Jane recommend in 2019?"* or *"When did we first say I love you?"*
- [ ] **Semantic Search**
    - Move beyond keyword search. Find messages by *concept*.
    - Example: Searching "food" finds messages about "pizza", "sushi", and "dinner".
- [ ] **Sentiment Rollercoaster**
    - Plot relationship sentiment over time (Moving Average).
    - Detect "breakup events" or "honeymoon phases" automatically.
- [ ] **Topic Modeling**
    - Auto-tag conversations: "Work", "relationships", "Gaming", "Politics".
    - "This week you talked mostly about: *Elden Ring*."

---

## 🛠️ Phase 4: The Universal Connector
*Support every platform where human connection happens.*

- [ ] **iMessage (macOS Local)**
    - Read directly from `~/Library/Messages/chat.db`.
    - No export required—real-time analysis.
- [ ] **Telegram**
    - Parser for Telegram's HTML/JSON export.
- [ ] **Discord**
    - Parser for Data Package Request (DPR).
    - Handle server channels vs DMs distinct logic.
- [ ] **Dating Apps (Tinder/Hinge/Bumble)**
    - Parser for GDPR data exports.
    - specialized metrics: "Match to Number Ratio", "Ghost Rate".
- [ ] **Google Hangouts / Chat**
    - Legacy parser for the old days.

---

## 🧪 Experimental / Brainstorming
*Wild ideas that might be cool.*

### "The Ghosting Graveyard" 🪦
- A specific view showing conversations that died.
- Metrics: "Last words sent", "Who killed it?", "Resurrection attempts".

### "Relationship Health Check" 🩺
- A score (0-100) based on reciprocity.
- Are you always the one initiating? Do they reply with one word?

### "Voice Note Transcriber" 🎙️
- Use OpenAI Whisper (locally) to transcribe all those long voice notes in WhatsApp/Messenger exports so they become searchable text.

### "Hardware Mode" 🥧
- Pre-built Docker container to run on a Raspberry Pi.
- Auto-ingest new export files from a network folder.
- Host the dashboard on the local network (`http://messenger-insights.local`).

### "PDF Book Generation" 📕
- Generate a printable PDF of a specific relationship.
- "The Story of Us" format—perfect for anniversaries.

---

## 🔭 Phase 5: The Frontier (Visionary Concepts)
*Features that push the boundaries of what a "message parser" can be.*

### 🧠 Psychometrics & Behavioral Analysis
- **"The Attachment Style Detector"**: Analyze patterns of "Anxious" (double texting, fast reply) vs "Avoidant" (long gaps, short replies) communication.
- **"The Flirtometer"**: Correlate *Emoji Density* + *Late Night Timestamps* + *Reply Speed* to detect romantic interest with >85% accuracy.
- **"Conflict Resolution Index"**: How fast does the sentiment bounce back to positive after a negative spike? Who usually apologizes first (first to say "sorry")?

### 💸 The Economics of Friendship
- **"Cost of Friendship"**: Regex parse messages for "$", "Venmo", "owe you", "dinner".
- **"The Moocher Metric"**: Who requests money vs who sends money?

### 🕸️ Network Science (Group Chats)
- **"The Bridge"**: Identify which friend connects two disparate friend groups.
- **"The Glue"**: Who leaves the group chat last? If this person leaves, the chat dies.
- **"Main Character Energy"**: Who gets the most replies per message sent?

### 🎨 Art & Philosophy
- **"Linguistic Drift" 🧬**: Visualize how you "become" your friends. Track slang adoption (e.g., when did you start saying "bet"?).
- **"The Digital Twin" 🤖**: Local LoRA model to simulate your friends.
- **"Sonification" 🎹**: Turn a relationship into a MIDI file. Pitch = Sentiment, Tempo = Message Frequency. Listen to the "sound" of your breakup.
- **"VR Memory Palace" 🥽**: WebXR timeline hallway.

### 🛡️ Digital Legacy
- **"Decentralized Time Capsule" 💊**: IPFS-encrypted threads that unlock in 10 years.
- **"The Erasure Utility"**: A "Men in Black" flashy-thing feature. Generates a script to *unsend* every message you ever sent to a specific person (via API or macro).

---

## 🐛 Technical Debt / Maintenance
- [ ] **Unit Tests**: Coverage is good, but need more edge cases for corrupt JSONs.
- [ ] **Performance**: Optimize `pandas` memory usage for 50GB+ ultra-massive datasets (maybe switch to `polars`?).
- [ ] **UI Themes**: Allow user to toggle between "Cyberpunk", "Light Mode", "Paper", and "Terminal".

---

## ⚡ Scalability Optimization (v3.0 Priority)

### The Problem
Currently, **all data is embedded directly in the HTML report**. For a typical export (~3,700 messages), this produces a ~200KB file that loads instantly. However, for power users with **10+ years of chat history** (100k+ messages), this approach has issues:

| Messages | Estimated Report Size | Load Time | Memory Usage |
|----------|----------------------|-----------|--------------|
| 3,700 | 200 KB | Instant | 10 MB |
| 50,000 | ~3 MB | 1-2 sec | 50 MB |
| 500,000 | ~30 MB | 5-10 sec | 200+ MB |
| 1,000,000+ | 60+ MB | 15+ sec | 500+ MB (browser may lag) |

### The Solution: On-Demand Data Loading

**Phase 1: Split Data from Template**
```
output/
├── report.html           # Lightweight shell (~50KB)
├── data/
│   ├── metadata.json     # Conversation list, basic stats
│   ├── timeline.json     # Pre-aggregated daily counts
│   ├── convs/
│   │   ├── alice.json    # Per-conversation activity data
│   │   ├── bob.json
│   │   └── group_chat.json
│   └── emojis/
│       ├── _global.json  # Global emoji counts
│       └── alice.json    # Per-conversation emoji data
```

**Phase 2: Lazy Loading in Frontend**
- On page load: Fetch only `metadata.json` and render dropdown
- On conversation select: `fetch('/data/convs/${convTitle}.json')`
- Charts render from fetched data, no redundant loading

**Phase 3: Streaming Aggregation**
- For 1M+ message datasets, pre-aggregate in Python (hourly buckets, top emojis only)
- Never load raw messages into browser memory

### Trade-offs
| Approach | Pros | Cons |
|----------|------|------|
| **Current (Single HTML)** | Works offline, single file to share | Large files for big datasets |
| **Split + Fetch** | Scalable, fast initial load | Requires local server or file:// CORS workaround |
| **WebSocket Streaming** | Real-time updates, lowest memory | Complex, server dependency |

### Recommended Path
1. **Short-term**: Add `--large` CLI flag that uses split data approach
2. **Medium-term**: Default to split data, bundle local Python server for viewing
3. **Long-term**: WebAssembly-based pandas for in-browser aggregation (no server)

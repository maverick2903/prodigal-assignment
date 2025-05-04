# 📞 Call Analysis Tool

A Streamlit application for analyzing customer service calls with features for compliance monitoring and call quality assessment.

## 📋 Overview

This tool provides automated analysis of call transcripts between agents and borrowers, focusing on three key areas:

1. **Profanity Detection** - Identifies if either party used inappropriate language
2. **Privacy & Compliance Violations** - Detects if agents shared sensitive information before verifying customer identity
3. **Call Quality Metrics** - Analyzes speaking time, silence periods, and overtalk

## 🔍 Features

### Entity Detection
- **Profanity Detection**
  - Pattern Matching: Uses regex patterns to identify explicit language
  - LLM-based: Uses Gemini AI to analyze conversation context and detect profanity

- **Privacy & Compliance**
  - Pattern Matching: Identifies patterns of sensitive information disclosure
  - LLM-based: Uses Gemini AI to analyze compliance with verification protocols

### Call Quality Metrics
- Visualizes call timelines with speaker attribution
- Calculates and displays:
  - Total call duration
  - Speaking time for each party
  - Silence periods
  - Overtalk (when both parties speak simultaneously)
  - Percentage distributions of call components

## 🛠️ Setup

### Prerequisites
- Python 3.7+
- Gemini API access (for LLM-based detection)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/call-analysis-tool.git
   cd call-analysis-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get a Gemini API key:
   - Go to [Google AI Studio](https://makersuite.google.com/)
   - Create a project and generate an API key
   - Save this key for use with the application

## 🚀 Usage

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Access the application in your browser (usually at http://localhost:8501)

3. In the sidebar, enter your Gemini API key (required for LLM-based analysis)

4. Upload a conversation JSON file in the following format:
   ```json
   [
     {
       "stime": 0.0,
       "etime": 5.2,
       "speaker": "Agent",
       "text": "Hello, this is customer service. How can I help you today?"
     },
     {
       "stime": 5.5,
       "etime": 10.3,
       "speaker": "Customer",
       "text": "Hi, I'm calling about my account balance."
     },
     ...
   ]
   ```

5. Select the analysis type:
   - Choose between Pattern Matching (faster) or LLM (more accurate)
   - Select the entity to analyze (Profanity or Privacy/Compliance)

6. View results in the Call Quality Metrics tab for visualization of the conversation flow


## 🧪 Project Structure

```
maverick2903-prodigal-assignment/
├── README.md
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── All_Conversations/          # Sample conversation files
├── task1_profanity/            # Profanity detection modules
│   ├── llm_detector.py         # Gemini-based detection
│   └── regex_detector.py       # Pattern-based detection
├── task2_privacy/              # Privacy violation detection
│   ├── llm_detector.py         # Gemini-based detection
│   └── regex_detector.py       # Pattern-based detection
└── task3_metrics/              # Call quality analysis
    └── call_quality.py         # Metrics calculation
```

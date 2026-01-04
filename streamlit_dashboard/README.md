# 🔥 Wildfire Detection Dashboard

Real-time wildfire monitoring dashboard built with Streamlit. 

## Features
- 🗺️ Interactive incident map
- 📊 Real-time analytics
- 📡 Device monitoring
- 🔔 Alert history

## Setup

1. Clone the repo
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Add secrets to `.streamlit/secrets.toml`:
   ```toml
   FIREBASE_SERVICE_ACCOUNT = '{ ... your JSON ... }'
   ```
4. Run locally:
   ```bash
   streamlit run app.py
   ```

## Deploy to Streamlit Cloud

1. Push to GitHub
2. Connect repo at [streamlit.io/cloud](https://streamlit.io/cloud)
3. Add secrets in dashboard settings
4. Deploy!  🚀
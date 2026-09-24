# Investor Research

A mobile-first Streamlit dashboard for tracking stocks and ETFs. It turns market data into plain-English reference zones, trend signals, momentum, risk context, company facts, and recent news.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run stock_app.py
```

## Deploy on Streamlit Community Cloud

1. Put `stock_app.py` and `requirements.txt` in the root of a public GitHub repository.
2. In Streamlit Community Cloud, choose **Deploy a public app from GitHub**.
3. Select the repository and `main` branch.
4. Set **Main file path** to `stock_app.py` and deploy.

Market data is fetched when the app loads or reruns. It is for research and education, not investment advice or trade execution.

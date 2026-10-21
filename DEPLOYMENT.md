# Deploy CardServ AI for a portfolio review

## Recommended host: Streamlit Community Cloud

This project uses Streamlit. Streamlit Community Cloud is the simplest hosting option for this app and provides a public `streamlit.app` URL on its free offering. Vercel's standard deployment model is oriented around web front ends and request-based functions; moving this project there would require a redesign or a separate service rather than deploying the existing Streamlit app directly.

## Before publishing

- Review the full repository and confirm that it contains no API keys, `.env` files, customer data, or private employer material.
- The project includes only synthetic contact records and fictional servicing-policy examples. Keep that boundary clear in the README and demo.
- The app works without an OpenAI key. Do not configure a key for a hiring-manager demo unless you specifically need the optional model path.
- Treat the public app as a portfolio demonstration, not an operational tool. The risk-control values, approvals, monitor signals, and incident entries are illustrative.

## Steps

1. Extract the project ZIP locally.
2. Create a new GitHub repository, for example `cardserv-ai-servicing-governance`, and push the **contents** of the `cardserv_ai_project` folder to the repository root (so `app.py` and `requirements.txt` are at the root).
3. Open <https://share.streamlit.io/> and sign in with GitHub.
4. Select **Create app**, choose the repository and branch, and set the main file path to `app.py`.
5. In advanced settings, select Python 3.12. No secrets are needed for the offline demo.
6. Deploy. Once the app is live, choose a concise subdomain if available, then open it in a private/incognito window to verify public access.
7. Share the resulting `https://<your-chosen-name>.streamlit.app` URL with the hiring manager.

## Local validation

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest -q
streamlit run app.py
```

## Operational limitations

Streamlit Community Cloud is suitable for a non-sensitive portfolio demo. Session state and local files should not be treated as a reliable durable governance database. If this were developed beyond a demo, replace session-only incident/decision capture with an approved database and access-controlled audit service, add authentication as appropriate, and have the relevant control owners approve the risk framework.

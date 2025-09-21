
## 🚀 AI-Powered Repo Migration Dashboard

This project automates the migration of Azure DevOps repositories to GitLab and converts Azure pipeline YAMLs into Jenkinsfiles using Azure OpenAI (GPT-4o). It provides a secure, single-folder Flask dashboard that handles repo import, pipeline conversion, and deployment guidance — all in one place.

---

### 🧩 Architecture Overview

```plaintext
User → Flask Web Form → GitLab Import API → GitLab Status Polling
     → Azure Repo (fetch azure-pipelines.yml)
     → Azure OpenAI (GPT-4o) → Jenkinsfile + Deployment Guide
     → HTML Output (Status + YAML + Jenkinsfile + Progress Bar)
```

<img width="784" height="358" alt="image" src="https://github.com/user-attachments/assets/0a3dd39f-1f2a-42b5-b854-247c1b9c8926" />


---

### 🛠️ Tech Stack

| Component        | Technology Used           |
|------------------|---------------------------|
| Frontend         | HTML + Flask Web Form     |
| Backend          | Python (Flask)            |
| Repo Import      | GitLab REST API           |
| Pipeline Fetch   | Azure DevOps REST API     |
| AI Conversion    | Azure OpenAI (GPT-4o)     |
| Output Rendering | Flask + HTML Templates    |

---

### 🔐 Secure Credential Management

All secrets are stored in a `.env` file and loaded via `python-dotenv`. This ensures:
- No hardcoded tokens
- Easy rotation and environment isolation
- Compatibility with air-gapped workflows

---

### 💡 Jenkinsfile Deployment Guide (Auto-Generated)

**Steps to Deploy Jenkinsfile:**
1. Copy the Jenkinsfile into your GitLab repo root.
2. Go to GitLab → CI/CD → Variables and define required build variables.

**Steps to Create Jenkins Pipeline:**
1. Open Jenkins → New Item → Pipeline
2. Set 'Pipeline script from SCM' → Git → enter your GitLab repo URL
3. Add GitLab credentials (PAT or SSH key)
4. Set branch to `main` and script path to `Jenkinsfile`
5. Define build variables like `DOTNET_VERSION`, `BUILD_CONFIG`, `API_KEY`
6. Optionally configure GitLab webhooks to trigger builds

---

### ✅ Features

- 🔄 GitLab import with status polling
- 📄 Azure pipeline YAML fetch
- 🤖 Jenkinsfile generation via GPT-4o
- 📊 Real-time progress bar
- 🔐 Secure `.env`-based credential loading
- 🧱 Single-folder, maintainable structure

---

### 📦 Future Enhancements

- Auto-commit Jenkinsfile to GitLab
- GitLab webhook setup for Jenkins triggers
- Role-based access for dashboard users
- Multi-repo batch migration support

---

### ✨ Why This Matters

This dashboard isn’t just a migration tool — it’s a blueprint for how AI can streamline DevOps workflows. By combining REST APIs, secure scripting, and LLM-powered conversion, it delivers a fast, reliable, and future-proof solution for CI/CD transitions.

---

Let me know if you'd like this README styled with badges, linked to your GitLab repo, or converted into a GitHub Pages landing page.

from flask import Flask, request, render_template_stringfrom dotenv import load_dotenv
from openai import AzureOpenAI
import os
import requests
import logging
import time

# Load environment variables
load_dotenv()
logging.basicConfig(level=logging.INFO)# Azure OpenAI clientclient = AzureOpenAI(
    api_key=os.getenv("AZURE_API_KEY"),
    api_version=os.getenv("AZURE_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_API_BASE")
)

# GitLab config
GITLAB_TOKEN = os.getenv("GITLAB_TOKEN")
GITLAB_GROUP_ID = int(os.getenv("GITLAB_GROUP_ID"))
GITLAB_API = os.getenv("GITLAB_API")

# Azure DevOps
AZURE_PAT = os.getenv("AZURE_PAT")
AZURE_USERNAME = os.getenv("AZURE_USERNAME", "shakil")

app = Flask(__name__)

@app.route('/repo_migrate/', methods=['GET', 'POST'])
def migrate():
    gitlab_status = ""
    azure_pipeline = ""
    jenkinsfile = ""
    progress = 0

    if request.method == 'POST':
        source_repo = request.form['sourceRepo'].strip()
        target_repo = request.form['targetRepo'].strip()
        repo_name = target_repo.rstrip('/').split('/')[-1]

        if "@" not in source_repo:
            source_repo = source_repo.replace("https://", f"https://{AZURE_USERNAME}:{AZURE_PAT}@")

        headers = { "PRIVATE-TOKEN": GITLAB_TOKEN }
        data = {
            "name": repo_name,
            "namespace_id": GITLAB_GROUP_ID,
            "import_url": source_repo
        }

        response = requests.post(GITLAB_API, headers=headers, data=data)
        logging.info(f"GitLab response: {response.status_code} - {response.text}")
        progress = 20

        if response.status_code != 201:
            gitlab_status = f"❌ GitLab import failed:\n{response.text}"
        else:
            gitlab_status = f"✅ GitLab import initiated for `{repo_name}`"
            project_url = f"https://gitlab.com/shakil-ai-poc/{repo_name}"
            logging.info(f"Expected GitLab project URL: {project_url}")

            import_status_url = f"https://gitlab.com/api/v4/projects/{GITLAB_GROUP_ID}%2F{repo_name}/import"
            for _ in range(10):
                time.sleep(2)
                status_response = requests.get(import_status_url, headers=headers)
                if status_response.status_code == 200:
                    status = status_response.json().get("status")
                    logging.info(f"Import status: {status}")
                    if status == "finished":
                        gitlab_status = f"✅ GitLab import completed for `{repo_name}`"
                        progress = 40
                        break
                    elif status == "failed":
                        gitlab_status = f"❌ GitLab import failed during processing"
                        progress = 100
                        return render_template_string(template,
                            gitlab_status=gitlab_status,
                            azure_pipeline=azure_pipeline,
                            jenkinsfile=jenkinsfile,
                            progress=progress
                        )
                progress += 5

            pipeline_url = f"https://dev.azure.com/23932140510/AI-POC/_apis/git/repositories/AI-POC/items?path=/azure-pipelines.yml&api-version=7.0"
            pipeline_response = requests.get(pipeline_url, auth=(AZURE_USERNAME, AZURE_PAT))
            progress = 60

            if pipeline_response.status_code == 200:
                azure_pipeline = pipeline_response.text
                progress = 80

                prompt = f"""Convert this Azure DevOps pipeline YAML to Jenkinsfile for a .NET build:\n{azure_pipeline}

Also include the following deployment instructions at the end:

✅ Steps to Deploy Jenkinsfile:
1. Copy the Jenkinsfile into your GitLab repo root.
2. Go to GitLab → CI/CD → Variables and define required build variables.

✅ Steps to Create Jenkins Pipeline:
1. Open Jenkins → New Item → Pipeline
2. Set 'Pipeline script from SCM' → Git → enter your GitLab repo URL
3. Add GitLab credentials (PAT or SSH key)
4. Set branch to 'main' and script path to 'Jenkinsfile'
5. Define build variables like DOTNET_VERSION, BUILD_CONFIG, API_KEY
6. Optionally configure webhooks in GitLab to trigger builds
"""

                try:
                    ai_response = client.chat.completions.create(
                        model=os.getenv("AZURE_DEPLOYMENT_MODEL"),
                        messages=[{"role": "user", "content": prompt}]
                    )
                    jenkinsfile = ai_response.choices[0].message.content
                    progress = 100
                except Exception as e:
                    jenkinsfile = f"⚠️ Jenkinsfile generation failed:\n{str(e)}"
                    progress = 100
            else:
                azure_pipeline = f"⚠️ Azure pipeline file not found:\n{pipeline_response.text}"
                progress = 100

    return render_template_string(template,
        gitlab_status=gitlab_status,
        azure_pipeline=azure_pipeline,
        jenkinsfile=jenkinsfile,
        progress=progress
    )

template = '''
<!DOCTYPE html>
<html>
<head>
  <title>Repo Migration</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background: linear-gradient(to right, #eef2f3, #8e9eab);
      padding: 40px;
    }
    .container {
      background-color: white;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.2);
      max-width: 1000px;
      margin: auto;
    }
    h2 {
      text-align: center;
      color: #333;
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 15px;
    }
    input[type="text"] {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border: 1px solid #ccc;
      border-radius: 5px;
    }
    button {
      margin-top: 20px;
      width: 100%;
      padding: 10px;
      background-color: #4CAF50;
      color: white;
      border: none;
      border-radius: 5px;
      cursor: pointer;
      font-size: 16px;
    }
    button:hover {
      background-color: #45a049;
    }
    .output-box {
      margin-top: 30px;
      padding: 20px;
      background-color: #f9f9f9;
      border-left: 5px solid #4CAF50;
      border-radius: 5px;
      white-space: pre-wrap;
      font-family: monospace;
    }
    #progress {
      margin-top: 20px;
      height: 25px;
      background-color: #ddd;
      border-radius: 5px;
      overflow: hidden;
      position: relative;
    }
    #progress-bar {
      height: 100%;
      background-color: #4CAF50;
      width: {{progress}}%;
      transition: width 0.5s ease-in-out;
    }
    #progress-label {
      position: absolute;
      width: 100%;
      text-align: center;
      line-height: 25px;
      font-weight: bold;
      color: #333;
    }
  </style>
</head>
<body>
  <div class="container">
    <h2>Repo Migration</h2>
    <form method="POST">
      <label>Source Repo (Azure):</label>
      <input type="text" name="sourceRepo" placeholder="https://dev.azure.com/...">
      <label>Target Repo (GitLab):</label>
      <input type="text" name="targetRepo" placeholder="https://gitlab.com/...">
      <button type="submit">Migrate & Convert</button>
    </form>

    <div id="progress">
      <div id="progress-bar"></div>
      <div id="progress-label">{{progress}}%</div>
    </div>

    {% if gitlab_status %}
      <div class="output-box"><strong>🔄 GitLab Import Status:</strong>\n{{gitlab_status}}</div>
    {% endif %}
    {% if azure_pipeline %}
      <div class="output-box"><strong>📄 Azure Pipeline YAML:</strong>\n{{azure_pipeline}}</div>
    {% endif %}
    {% if jenkinsfile %}
      <div class="output-box"><strong>🚀 Jenkinsfile Output + Deployment Steps:</strong>\n{{jenkinsfile}}</div>
    {% endif %}
  </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

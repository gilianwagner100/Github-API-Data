import os
from dotenv import load_dotenv

load_dotenv()

# Github
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_BASE_URL = "https://api.github.com"
HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2026-03-10",
}

# GCP / BigQuery


# Repo Lists
LEGACY_REPOS = ['fastmachinelearning/hls4ml', 'elyra-ai/elyra', 'brannondorsey/PassGAN', 'r9y9/deepvoice3_pytorch', 'robertmartin8/MachineLearningStocks', 'neonwatty/machine-learning-refined', 'VivekPa/AIAlpha', 'jakeret/tf_unet', 'GPflow/GPflow', 'AutoViML/AutoViz', 'Theano/Theano', 'google-deepmind/sonnet', 'drivendataorg/cookiecutter-data-science', 'vwxyzjn/cleanrl', 'yzhao062/pyod', 'pycaret/pycaret', 'sktime/sktime', 'tflearn/tflearn', 'MorvanZhou/Reinforcement-learning-with-tensorflow', 'unit8co/darts', 'apache/airflow', 'streamlit/streamlit', 'gradio-app/gradio', 'ray-project/ray', 'explosion/spaCy', 'eriklindernoren/ML-From-Scratch', 'Lightning-AI/pytorch-lightning', 'donnemartin/data-science-ipython-notebooks', 'd2l-ai/d2l-en', 'mlflow/mlflow', 'pytorch/pytorch', 'd2l-ai/d2l-zh', 'scikit-learn/scikit-learn', 'keras-team/keras', 'ageitgey/face_recognition', 'deepfakes/faceswap']
LLM_REPOS = ['roboterax/humanoid-gym', 'eosphoros-ai/DB-GPT-Hub', 'AgentOps-AI/tokencost', 'ymcui/Chinese-LLaMA-Alpaca-3', 'jimmc414/onefilellm', 'BetaStreetOmnis/xhs_ai_publisher', 'nottelabs/notte', 'superlinked/sie', 'guy-hartstein/company-research-agent', 'FoundationVision/LlamaGen', 'Arize-ai/phoenix', 'microsoft/magentic-ui', 'langchain-ai/open-swe', 'linyqh/NarratoAI', 'xorbitsai/inference', '0x4m4/hexstrike-ai', 'mrexodia/ida-pro-mcp', 'OpenSPG/KAG', 'microsoft/UFO', 'aliasrobotics/cai', 'run-llama/llama_index', 'BerriAI/litellm', 'hesreallyhim/awesome-claude-code', '2noise/ChatTTS', 'QuivrHQ/quivr', 'chatchat-space/Langchain-Chatchat', 'LAION-AI/Open-Assistant', 'google/langextract', 'HKUDS/LightRAG', 'github/awesome-copilot', 'Significant-Gravitas/AutoGPT', 'NousResearch/hermes-agent', 'open-webui/open-webui', 'microsoft/markitdown', 'Comfy-Org/ComfyUI', 'Shubhamsaboo/awesome-llm-apps', 'github/spec-kit', 'browser-use/browser-use', 'hacksider/Deep-Live-Cam', 'infiniflow/ragflow']
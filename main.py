import os
import subprocess
import autogen
from code_review_agent import CodeReviewAgent
from static_analyzer_agent import StaticAnalyzerAgent

# Disable Docker usage
os.environ['AUTOGEN_USE_DOCKER'] = '0'

# Configure repository path
GIT_REPO_PATH = ""

def get_latest_commit(repo_path):
    try:
        commit_hash = subprocess.check_output(
            ["git", "-C", repo_path, "rev-parse", "HEAD"]
        ).strip().decode("utf-8")
        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Error fetching latest commit: {e}")
        return None

def get_commit_diff(repo_path, commit_hash):
    try:
        diff = subprocess.check_output(
            ["git", "-C", repo_path, "diff", f"{commit_hash}~1", commit_hash]
        ).decode("utf-8")
        return diff
    except subprocess.CalledProcessError as e:
        print(f"Error fetching commit diff: {e}")
        return None

def main():
    logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
    print("Logging session ID: " + str(logging_session_id))
    
    local_llm_config = {
        "config_list": [
            {
                "model": "llama3.2",
                "api_key": "ollama",
                "base_url": "http://localhost:11434/v1",
                "price": [0, 0],
            }
        ],
        "cache_seed": None,
    }
    
    review_agent = CodeReviewAgent(llm_config=local_llm_config, name="code_review_agent")
    analyze_agent = StaticAnalyzerAgent(llm_config=local_llm_config, name="static_analyzer_agent")

    commit_hash = get_latest_commit(GIT_REPO_PATH)
    if not commit_hash:
        print("Could not fetch the latest commit.")
        return

    print(f"Latest commit hash: {commit_hash}")

    diff = get_commit_diff(GIT_REPO_PATH, commit_hash)
    if not diff:
        print("Could not fetch the commit diff.")
        return

    print("Commit diff fetched successfully.")

    feedback = review_agent.review_code(diff)
    analysis = analyze_agent.static_analysis(diff)

    print("\nCode Review Feedback:")
    print(feedback)

    print("\nStatic Analysis Feedback:")
    print(analysis)

    autogen.runtime_logging.stop()

if __name__ == "__main__":
    main()
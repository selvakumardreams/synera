import os
import subprocess
import autogen

# Disable Docker usage
os.environ['AUTOGEN_USE_DOCKER'] = '0'

# Configure repository path
GIT_REPO_PATH = ""

class CodeReviewAgent(autogen.ConversableAgent):
    def __init__(self, llm_config, name):
        super().__init__(llm_config=llm_config, name=name)
        self.user_proxy = autogen.UserProxyAgent(name="user_proxy", 
                                                 code_execution_config=False, 
                                                 human_input_mode="NEVER", 
                                                 max_consecutive_auto_reply=1,
                                                 is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"])

    def review_code(self, diff):
        # Define a prompt for the code review task
        prompt = f"""
        You are a code review assistant. Please analyze the following code diff and provide:
        1. A summary of the changes.
        2. Any issues, bugs, or anti-patterns present.
        3. Suggestions for improvements.

        "Return 'TERMINATE' when the task is done." Here is the code diff:
        {diff}
        """

        print("Sending the following prompt to the user proxy:")
        print(prompt)

        # Use the user proxy to get a response from the model
        response = self.user_proxy.initiate_chat(recipient=self, message=prompt)
        
        return response


# Helper functions
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

# Main function
def main():

    logging_session_id = autogen.runtime_logging.start(config={"dbname": "logs.db"})
    print("Logging session ID: " + str(logging_session_id))
    
    local_llm_config = {

        "config_list": [
            {
                "model": "llama3.2",  # 
                "api_key": "ollama",  # 
                "base_url": "http://localhost:11434/v1",  # Your URL
                "price": [0, 0],  # Put in price per 1K tokens [prompt, response] as free!
            }
        ],
        "cache_seed": None,  # Turns off caching, useful for testing different models
    }
    
    # Create an instance of the CodeReviewAgent
    review_agent = CodeReviewAgent(llm_config=local_llm_config, name="code_review_agent")

    # Step 1: Fetch the latest commit
    commit_hash = get_latest_commit(GIT_REPO_PATH)
    if not commit_hash:
        print("Could not fetch the latest commit.")
        return

    print(f"Latest commit hash: {commit_hash}")

    # Step 2: Get the commit diff
    diff = get_commit_diff(GIT_REPO_PATH, commit_hash)
    if not diff:
        print("Could not fetch the commit diff.")
        return

    print("Commit diff fetched successfully.")

    # # Example diff to review
    example_diff = """
    def add(a, b):
        return a + b

    def subtract(a, b):
        return a - b
    """
    # Step 3: Perform code review
    feedback = review_agent.review_code(example_diff)
    print("\nCode Review Feedback:")
    print(feedback)

    autogen.runtime_logging.stop()

if __name__ == "__main__":
    main()

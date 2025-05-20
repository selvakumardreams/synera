import autogen

class CodeReviewAgent(autogen.ConversableAgent):
    def __init__(self, llm_config, name):
        super().__init__(llm_config=llm_config, name=name)
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy", 
            code_execution_config=False, 
            human_input_mode="NEVER", 
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
        )

    def review_code(self, diff):
        prompt = f"""
            You are a senior software engineer performing a professional code review. 
            Your job is to provide **clear, concise, human-readable feedback** in the style of comments on a pull request.

            For each issue you find:
            - Describe *what* the issue is.
            - Explain *why* it matters (e.g., readability, performance, correctness, security, or style).
            - Suggest a fix or improvement if possible.
            - Be constructive, respectful, and specific.

            Use bullet points or numbered lists if there are multiple issues.

            Format your response as if you're leaving comments on a GitHub pull request.

            Be concise but helpful.

        "Return 'TERMINATE' when the task is done." Here is the code diff:
        {diff}
        """

        print("Sending the following prompt to the user proxy:")
        print(prompt)

        response = self.user_proxy.initiate_chat(recipient=self, message=prompt)
        return response
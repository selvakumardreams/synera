import autogen

class StaticAnalyzerAgent(autogen.ConversableAgent):
    def __init__(self, llm_config, name):
        super().__init__(llm_config=llm_config, name=name)
        self.user_proxy = autogen.UserProxyAgent(
            name="user_proxy", 
            code_execution_config=False, 
            human_input_mode="NEVER", 
            max_consecutive_auto_reply=1,
            is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"]
        )

    def static_analysis(self, diff):
        prompt = f"""
            You are a static analysis engine. Review the code and return issues like:
            - Unused imports
            - Missing docstrings
            - PEP8 violations
            - Type annotation suggestions
            Format your response like a linter: Line number, issue type, message.
            {diff}
            """
        print("Sending the following prompt to the user proxy:")
        print(prompt)

        response = self.user_proxy.initiate_chat(recipient=self, message=prompt)
        return response

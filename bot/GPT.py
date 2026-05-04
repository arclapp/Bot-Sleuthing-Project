import os
from typing import Optional, List, Dict
from dotenv import load_dotenv
from openai import OpenAI

class GPT():
    def __init__(self, role_description:str, model: Optional[str] = None, temperature:float=1.0):
        """
        Initialize the LLM  with a system role description.

        Args:
            role_description (str): A description of the assistant's role or behavior.
            model (Optional[str]): Optional model override. If not provided, uses
                OPENAI_LLM_MODEL from the environment or defaults to 'gpt-5-nano'.
            temperature (float): Temperature of responses (0.0: Less creative, 2.0: More creative)
        """
        
        self._chat_history: List[Dict] = [{
            "role": "developer", 
            "content": role_description,
        }]
        self._model = model 
        self._temperature = temperature

        load_dotenv(override=False)

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment (.env).")

        self._client = OpenAI(api_key=api_key)
    
    def history(self, include_fewshot:bool = False) -> list[dict]:
        """
        Return the chat history.

        Args:
            include_fewshot (bool): Whether to include few-shot examples in
                the returned history. Defaults to False.

        Returns:
            list[dict]: The conversation history in the format:
                [{"role": "", "content": ""}, ...]
        """

        if include_fewshot:
            return list(self._chat_history)

        filtered: List[Dict] = []
        for msg in self._chat_history:
            if msg.get("fewshot", False):
                continue
            filtered.append(msg)
        return filtered


    def prompt(self, input:str) -> str:
        """
        Prompt the LLM, and include prior prompting history and context
        
        Args:
            input (str): The user prompt input
           
        Returns:
            str: Assistant reply content.
        """

        messages: List[Dict] = self.history(include_fewshot=True)

        user_msg = {"role": "user", "content": input}

        messages = messages + [user_msg]


        params = dict(model=self._model, messages=messages, temperature=self._temperature)

        resp = self._client.chat.completions.create(**params)
        reply = resp.choices[0].message.content or ""


        self._chat_history.append(user_msg)
        self._chat_history.append({
            "role": "assistant",
            "content": reply,
        })

        return reply



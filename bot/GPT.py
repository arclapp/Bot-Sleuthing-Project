import os
import re
import json
from planning.llm.llm import LLM
from typing import Optional, List, Dict
from dotenv import load_dotenv

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

class GPT():
    def __init__(self, role_description:str, model: Optional[str] = None):
        """
        Initialize the LLM  with a system role description.

        Args:
            role_description (str): A description of the assistant's role or behavior.
            model (Optional[str]): Optional model override. If not provided, uses
                OPENAI_LLM_MODEL from the environment or defaults to 'gpt-5-nano'.
            save_history (bool): True if each prompt to LLM should include the prior
                chat history
        """
        
        self._chat_history: List[Dict] = [{
            "role": "developer", 
            "content": role_description,
        }]
        self._model = model 

        load_dotenv(override=False)

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY not found in environment (.env).")

        self._client = OpenAI(api_key=api_key)
    
    

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


        params = dict(model=self._model, messages=messages)

        resp = self._client.chat.completions.create(**params)
        reply = resp.choices[0].message.content or ""

        if self._save_history:
            self._chat_history.append(user_msg)
            self._chat_history.append({
                "role": "assistant",
                "content": reply,
            })

        return reply



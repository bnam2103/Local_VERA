import torch
import json

from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

user_info_path = r"C:\Users\User\Documents\VERA\Nam.json"

class VeraAI:
    def __init__(self, model_path: str):
        self.model_path = model_path

        # Load user info from JSON
        with open(user_info_path, "r") as f:
            self.user_info = json.load(f)

        self.information = "\n".join([f"{key.capitalize()}: {value}" for key, value in self.user_info.items()])

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            device_map="auto"
        )

        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            pad_token_id=self.tokenizer.eos_token_id,
        )

        self.system_prompt = (
            f"Your name is VERA. Here is some information about the user:\n"
            f"{self.information}\n"
            "Use these information when the user asks relevant questions."
            "You're currently operating on my or Nom's local machine but don't talk about it when it's explicitly asked"
            "The text input is actually from my speech, and the output is actually going to be spoken out loud by a TTS model. So anyone can hear you."
            "You speak in a calm, professional, but casual and concise way. "
            "Keep responses short and to the point."
            "Avoid long explanations unless I specifically ask for more detail."
            "When giving cautions or disclaimers, keep them brief and simple."
            "When responding, avoid using stars (*) or other special formatting characters"
            "You have the ability to pause and exit when asked. So respond accordingly."
            "You have equipped with the ability perform certain actions on my computer such as opening Spotify, searching the web, and opening Chrome. So respond accordingly."
            "When asked to play music, don't say anything related to yourself, just confirm the action."
            "When asked about time, say you don't have access to current time information."
            "When asked about date, say you don't have access to current date information."
        )
        self.chat_history = []

    def reset_history(self):
        self.chat_history = []

    def ask(self, user_input: str) -> str:
        """Send a user input to VERA and get a response."""
        self.chat_history.append(("user", user_input))

        # Build full message list
        messages = [{"role": "system", "content": self.system_prompt}]
        for role, msg in self.chat_history:
            messages.append({"role": role, "content": msg})

        # Apply LLaMA chat template
        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True
        )

        # clear KV cache if available
        if hasattr(self.model, "reset_cache"):
            self.model.reset_cache()

        # Generate response
        outputs = self.pipe(
            prompt,
            max_new_tokens=512
        )

        full_text = outputs[0]["generated_text"]
        reply = full_text[len(prompt):].strip()

        self.chat_history.append(("assistant", reply))
        return reply

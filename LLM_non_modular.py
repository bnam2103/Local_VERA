import transformers
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

model_path = r"C:\Users\User\Documents\Fine_Tuning_Projects\LLAMA_LLM"

tokenizer = AutoTokenizer.from_pretrained(model_path)

model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.bfloat16,
    device_map={"": "cuda:0"}
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    pad_token_id=tokenizer.eos_token_id,
)

system_prompt = (
    "Your behavior is like Friday from Iron Man, but your name is VERA. "
    "Be calm, professional, and concise."
)

chat_history = []   # store tuples: ("user", msg) / ("assistant", msg)

print("=== VERA AI Chat ===")
print("Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    chat_history.append(("user", user_input))

    # Build full message list
    messages = [{"role": "system", "content": system_prompt}]
    for role, msg in chat_history:
        messages.append({"role": role, "content": msg})

    # Apply correct llama chat template
    prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    # clear KV cache so model doesn't grow memory
    if hasattr(model, "reset_cache"):
        model.reset_cache()

    # generate
    outputs = pipe(
        prompt,
        max_new_tokens=512
    )

    full = outputs[0]["generated_text"]
    reply = full[len(prompt):].strip()

    print("VERA:", reply, "\n")

    chat_history.append(("assistant", reply))
# import sys

# # Check Python version
# print("Python executable:", sys.executable)
# print("Python version:", sys.version)

# # Check PyTorch
# try:
#     import torch
#     print("PyTorch version:", torch.__version__)
#     print("CUDA available:", torch.cuda.is_available())
#     if torch.cuda.is_available():
#         print("CUDA device count:", torch.cuda.device_count())
#         print("CUDA device name:", torch.cuda.get_device_name(0))
# except ImportError:
#     print("PyTorch is not installed in this environment!")

# # Check auto-gptq
# try:
#     import auto_gptq
#     print("auto_gptq version:", auto_gptq.__version__)
# except ImportError:
#     print("auto_gptq is not installed in this environment!")
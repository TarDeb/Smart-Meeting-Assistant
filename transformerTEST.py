<<<<<<< HEAD
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Use the smaller GPT-Neo model
MODEL_NAME = "EleutherAI/gpt-neo-125M"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Set the pad token to the EOS token if not already defined
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def generate_text(prompt, max_length=100):
    # Tokenize the input prompt with padding and truncation
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    
    # Generate text without tracking gradients (improves performance on CPU)
    with torch.no_grad():
        output = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=max_length,
            do_sample=True,  # Enables sampling for varied outputs
            top_p=0.95,      # Nucleus sampling for diversity
            top_k=50         # Consider only the top 50 tokens at each step
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    generated_text = generate_text(prompt)
    print("\nGenerated Text:\n", generated_text)
=======
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Use the smaller GPT-Neo model
MODEL_NAME = "EleutherAI/gpt-neo-125M"

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

# Set the pad token to the EOS token if not already defined
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

def generate_text(prompt, max_length=100):
    # Tokenize the input prompt with padding and truncation
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True)
    
    # Generate text without tracking gradients (improves performance on CPU)
    with torch.no_grad():
        output = model.generate(
            input_ids=inputs.input_ids,
            attention_mask=inputs.attention_mask,
            max_length=max_length,
            do_sample=True,  # Enables sampling for varied outputs
            top_p=0.95,      # Nucleus sampling for diversity
            top_k=50         # Consider only the top 50 tokens at each step
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    generated_text = generate_text(prompt)
    print("\nGenerated Text:\n", generated_text)
>>>>>>> 3bac854e4f4370cb0e196d3fab9eaac203402b44

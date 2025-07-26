from transformers import pipeline

# Load the GPT-2 model for text generation
gpt2_pipeline = pipeline("text-generation", model="gpt2")

# Define a contextual prompt to guide the assistant
BASE_PROMPT = (
    "You are a helpful assistant for a stock price forecasting website called ForeStock. "
    "You help users understand stock market terms, how stock predictions work, what affects stock prices, "
    "and answer basic finance and investment questions. "
    "Here is what the user asked:\nUser: "
)

def generate_reply(user_input):
    """
    Generate a short and concise reply using GPT-2 with context for a stock forecasting assistant.
    """
    try:
        prompt = BASE_PROMPT + user_input + "\nAssistant:"
        response = gpt2_pipeline(prompt, max_length=100, num_return_sequences=1)
        generated_text = response[0]['generated_text']

        # Extract only the assistant's response after the prompt
        assistant_reply = generated_text.split("Assistant:")[-1].strip()

        # Clean up any trailing user input echoes
        if "User:" in assistant_reply:
            assistant_reply = assistant_reply.split("User:")[0].strip()

        return assistant_reply
    except Exception as e:
        print(f"Error generating reply: {e}")
        return "I'm sorry, I couldn't process your request. Please try again later."

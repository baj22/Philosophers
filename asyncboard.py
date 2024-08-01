import streamlit as st
import asyncio
import json
from openai import AsyncOpenAI

# Initialize OpenAI client
client = AsyncOpenAI()

# Load configuration from JSON file
with open("config.json", "r") as file:
    config = json.load(file)

# Set page configuration using loaded config
st.set_page_config(
    page_title=config["page_title"],
    layout="wide",
)

# Set the title from the config
st.title(config["advisory_board_name"])

# Move the text box under the title
user_input = st.text_area("Enter your question or topic:")

# Button to generate advice
generate = st.button("Get Advice")

# Define advisors from the loaded config
advisors = config["advisors"]

# Create columns for advisors
columns = st.columns(len(advisors))
placeholders = [col.empty() for col in columns]

# Function to generate and stream advice
async def get_advice(placeholder, advisor):
    # Stream response from OpenAI API
    stream = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": advisor['role'] + " Answer all questions in the style of your personality. Make the answer brief but recognizable as the character."},
            {"role": "user", "content": user_input},
        ],
        stream=True
    )
    streamed_text = ""
    async for chunk in stream:
        chunk_content = chunk.choices[0].delta.content
        if chunk_content is not None:
            streamed_text += chunk_content
            placeholder.info(streamed_text)

# Function to run all advisors asynchronously
async def main():
    tasks = []
    for advisor, placeholder in zip(advisors, placeholders):
        # Display advisor's name and profile picture at the top of their column
        with placeholder.container():
            st.image(f"images/{advisor['image_filename']}", width=150)
            st.subheader(advisor['name'])
            advice_placeholder = st.empty()
            # Append task to list of async tasks
            tasks.append(get_advice(advice_placeholder, advisor))
    await asyncio.gather(*tasks)

# Check if user input is provided and button is clicked
if generate:
    if user_input.strip() == "":
        st.warning("Please enter a topic or question.")
    else:
        asyncio.run(main())
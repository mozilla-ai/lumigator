"""Based on https://github.com/vllm-project/vllm/blob/main/examples/gradio_openai_chatbot_webserver.py"""

import logging
import re

import gradio as gr
import requests

logger = logging.getLogger(__name__)


def predict(message, history, threshold):
    models = [
        {"name": "gpt-4o-mini", "color": "#1E90FF", "regex": r"^gpt-4o-mini-"},  # Dodger Blue
        {"name": "gpt-4o", "color": "#FF4500", "regex": r"^gpt-4o-(?!mini-)"},  # Orange Red
    ]

    url = "http://localhost:8000/api/v1/llm_router/"
    params = {
        "prompt": message,
        "threshold": threshold,
        "router_url": "http://10.16.2.93",
        "dry_run": False,
    }

    response = requests.get(url, params=params)
    result = response.json()

    # Try to find a matching model using regex
    for model in models:
        if re.match(model["regex"], result["model"]):
            selected_model = model
            break

    # Create model label with color
    model_label = f'<span style="color:{selected_model["color"]}; font-weight:bold;">{selected_model["name"]}</span>'

    # Construct the response with model label
    response = f"{model_label}\n {result['choices'][0]['message']['content']}"
    return response


# Create and launch a chat interface with Gradio
gr.ChatInterface(
    predict,
    additional_inputs=[
        gr.Number(label="Threshold", value=0.5),
    ],
).queue().launch(server_name="0.0.0.0", server_port=8081)

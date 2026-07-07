import time

from openai import OpenAI

from .config import MODEL, SYSTEM_PROMPT, TONE_TEMPERATURES, BriefOutput, build_user_prompt


def generate_brief(data):
    client = OpenAI()

    start = time.perf_counter()
    response = client.responses.parse(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=build_user_prompt(data),
        text_format=BriefOutput,
        temperature=TONE_TEMPERATURES[data["tone"]],
        max_output_tokens=800,
    )
    latency_ms = round((time.perf_counter() - start) * 1000)

    ai_response = response.output_parsed
    if len(ai_response.angles) != 3 or len(ai_response.criteria) != 3:
        raise ValueError("Model returned an unexpected number of angles/criteria")

    usage = response.usage
    return {
        **ai_response.model_dump(),
        "stats": {
            "model": response.model,
            "prompt_tokens": usage.input_tokens,
            "completion_tokens": usage.output_tokens,
            "total_tokens": usage.total_tokens,
            "finish_reason": response.status,
            "latency_ms": latency_ms,
        },
    }

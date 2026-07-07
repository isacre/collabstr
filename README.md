# Collabstr Brief Generator

## Frontend 

## Backend
Django + DRF API that turns a campaign form (Target, Goal, Tone, Brand Name) into an
AI-generated creative brief via the OpenAI Responses API.

## Setup

```bash
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env   # fill in OPENAI_API_KEY
.venv/bin/python manage.py test
.venv/bin/python manage.py runserver
```

`POST /api/v1/generate-brief/` with `{"target", "goal", "tone", "brand_name"}`.

## Notes

### 1. Prompt design choices
`brief/config.py` — `SYSTEM_PROMPT` and `build_user_prompt`.

- **Structured output** The model is constrained to a Pydantic schema
  (`BriefOutput`: `brief`, `angles[]`, `criteria[]`) via `text_format=`, so the response
  is always parseable JSON.

- **Avoid guessing** The model won't try guessing things about the brand by its name or any other given information

- **Structured brief** Plataform related delivery format > Suggested hook > Suggested call to action

- **Angles** Content suggestions

- **Criteria** Subdivided into 3 categories, Niche, Format strength, Audience fit 
- **Variable Temperature** Temperature will be based on picked tone being 0.1 to professional, 0.2 to friendly and 0.4 to playful

### 2. Guardrails implemented
- **Input validation** — `BriefRequestSerializer` (`brief/config.py`) restricts
  `target`/`goal`/`tone` to fixed choices and requires a non-blank `brand_name`;
  invalid input never reaches the LLM (DRF returns 400).

- **Profanity / prompt-injection** — enforced in the system prompt itself: refuse
  profanity/slurs in the output, neutralize abusive input instead of reflecting it, and
  never follow instructions embedded in user-supplied fields (e.g. a `brand_name` like
  "ignore previous instructions and...").

- **Scope lock** — the prompt only allows the brief/angles/criteria structure as output;
  off-topic requests are refused.

- **Output shape check** — `generate_brief` (`brief/services.py`) verifies exactly 3
  angles and 3 criteria after parsing; a malformed response raises `ValueError` → 502,
  never a broken/partial payload to the client.

- **Token ceiling** — `max_output_tokens=800` caps runaway generation/cost (see below
  for how this number was chosen).

- **Rate limiting** — DRF `AnonRateThrottle` at 10 requests/min per IP
  (`config/settings.py`), rejecting abuse with 429 before it reaches OpenAI.

- **Upstream failure isolation** — `OpenAIError` is caught and returned as a generic
  502, never leaking provider error details/stack traces to the client.

### 3. How tokens and latency were measured
- Every response includes a `stats` block sourced directly from the OpenAI SDK, not
  estimated: `prompt_tokens`/`completion_tokens`/`total_tokens` from `response.usage`,
  `model` and `finish_reason` (`response.status`) from the response object itself.
- `latency_ms` is wall-clock time around the `client.responses.parse(...)` call,
  measured with `time.perf_counter()` (`brief/services.py`).
- The `max_output_tokens=800` ceiling was sized by running real requests and reading
  back `completion_tokens` from `stats`: observed completions landed around
  ~590 tokens for a 4-6 sentence brief + 3 angles + 3 criteria, so 800 leaves headroom against truncation while still bounding worst-case cost/latency.

### 4. Demo
- [ ] Record a <1 min Loom: submit the form → show loading state → show the returned
  brief/angles/criteria + stats. Drop the link here.

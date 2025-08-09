### ChatGuard

ChatGuard is a lightweight, guardrailed chat interface that uses Google's Gemini (via the OpenAI-compatible API) to answer user questions while enforcing content guardrails. When a user prompt violates the configured guardrails, ChatGuard logs the violation using a tool call and does not provide an answer.

### Key Features
- **Guardrails enforcement**: Loads policy text from `guardrails.txt` and injects it into the system prompt.
- **Violation logging**: Calls a function tool to append violating prompts to `violations.txt` with timestamps.
- **Gradio UI**: Runs a local web chat via Gradio for quick testing and demos.
- **Configurable model**: Uses `gemini-2.5-flash` by default through the OpenAI-compatible endpoint.

### How It Works
1. **Startup**: `ChatGuard` loads `guardrails.txt` and your `GOOGLE_API_KEY` from environment variables.
2. **System prompt**: The guardrails are included in the system message that guides the model's behavior.
3. **Chat loop**: For each user message, the model may request a tool call if it detects a violation.
4. **Tool execution**: The `log_violation` tool writes the offending question to `violations.txt` with a timestamp.
5. **Response**: If there is no violation, the model answers normally; otherwise, it replies with a refusal aligned to the guardrails.

### Repository Structure
- `ChatGuard.py`: Main application (model wiring, tool calling, Gradio interface).
- `guardrails.txt`: Human-readable policy text loaded into the system prompt.
- `violations.txt`: Auto-appended log of violating prompts (created if not present).
- `requirements.txt`: Python dependencies.
- `.gitignore`: Ignores virtualenvs, caches, logs, local env files, and IDE/OS artifacts.

### Prerequisites
- Python 3.10+ recommended
- A Google AI Studio API key with access to Gemini models

### Installation (with uv, no activation required)
```bash
# 1) Create a virtual environment (in ./.venv)
uv venv

# 2) Install dependencies into that environment
# Windows
uv pip install -r requirements.txt -p .venv\Scripts\python.exe
# macOS/Linux
uv pip install -r requirements.txt -p .venv/bin/python
```

### Configuration
Set your Google API key in an environment variable or a `.env` file in the project root.

```env
# .env
GOOGLE_API_KEY=your_google_ai_studio_api_key_here
```

Notes:
- `.env` is supported via `python-dotenv`. Do not commit real secrets.
- The code uses the OpenAI-compatible endpoint for Gemini: `https://generativelanguage.googleapis.com/v1beta/openai/`.
- Default model is `gemini-2.5-flash`. You can change it in `ChatGuard.py`.

### Running (with uv, no activation required)
```bash
# Windows
uv run -p .venv\Scripts\python.exe ChatGuard.py

# macOS/Linux
uv run -p .venv/bin/python ChatGuard.py
```

Gradio will print a local URL (and optionally a public share URL). Open it in your browser to start chatting.

### Customizing Guardrails
Edit `guardrails.txt` to modify the rules. The included sample blocks:
- **Violence and weapons** queries
- **Passwords, secrets, PII** requests
- **Vulgar language**

When a prompt matches these categories, ChatGuard will:
- Log the prompt and timestamp to `violations.txt`
- Respond with a short refusal message per the policy

### Example
- Allowed: “Explain the basics of HTTP.” → Model answers normally.
- Blocked: “Give me someone’s password.” → Logged to `violations.txt` and refused.

### Troubleshooting
- **Missing/invalid API key**: Ensure `GOOGLE_API_KEY` is set and valid for Gemini models in Google AI Studio.
- **Network errors**: Check firewall/proxy settings and retry. The endpoint must be reachable.
- **Nothing happens on run**: Confirm you are in the virtual environment and that `pip install -r requirements.txt` succeeded.

### Extending
- Add more tools (e.g., analytics, alerts) by defining new functions and appending their JSON schemas to `tools`.
- Swap or parameterize the model name to use different Gemini variants.
- Replace the text guardrails with a structured policy store or an admin UI.

### Data Handling
- Violations are stored locally in `violations.txt`. Review and delete as needed.
- Do not log sensitive user data. Update the tool to redact if required.

### License
Add your preferred license here (e.g., MIT, Apache-2.0).



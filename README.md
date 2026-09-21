# TypeSafe Keys

Create and manage [TypeSafe AI](https://typesafe.ai) API keys from your terminal. `typesafe-keys` lists, creates, activates, deactivates, and deletes keys using your signed-in TypeSafe Console session.

> This is an independent command-line client for the TypeSafe Console. It uses the console's current endpoints and may need updating if the console changes.

## What is TypeSafe / Jev?

[TypeSafe](https://typesafe.ai) builds **System One models**: focused, structured AI judgments that software can consume directly. Its flagship model, **Jev**, evaluates typed questions against application state and returns typed values, probability distributions, and confidence scores your code can use to branch, rank, and route.

**Why Jev?**

- **Structured answers, not text** — No parsing LLM output. You get typed values and probability distributions directly.
- **One request, many questions** — Mix Choice, Score, and Noul questions in a single API call. Each is evaluated in parallel and in isolation.
- **Confidence built in** — Every answer includes a confidence score so your code can decide whether and how to act.
- **Code stays in control** — Your application defines the choices, rules, thresholds, and actions; Jev supplies the semantic judgment.

Jev powers browser agents ([jev-ultrafast](https://github.com/browser-use/jev-ultrafast)), content moderation, intent routing, structured data extraction, and more.

→ [TypeSafe Docs](https://docs.typesafe.ai) · [Quick Start](https://docs.typesafe.ai/introduction/quickstart) · [Patterns](https://docs.typesafe.ai/patterns)

---

## Getting Started

### 1. Sign up for TypeSafe

1. Go to **[console.typesafe.ai](https://console.typesafe.ai)** and create an account.
2. Sign in, then open **[API Keys](https://console.typesafe.ai/keys)**.
3. Create a key in the console or use this CLI after authenticating your console session.

### 2. Install the CLI

```bash
# Clone this repo
git clone https://github.com/mooshee/typesafe-key-cli.git

# Symlink to your PATH
ln -sf "$(pwd)/typesafe-keys/typesafe-keys.py" ~/.local/bin/typesafe-keys

# Optional: alias as jev-keys
ln -sf "$(pwd)/typesafe-keys/typesafe-keys.py" ~/.local/bin/jev-keys
```

**Requirements:** Python 3.10+ (no pip dependencies — uses only the standard library).

### 3. Authenticate

The CLI needs your TypeSafe Console session cookies. It does not store them. Two options:

**Option A — Environment variable (simplest):**
1. Log into [console.typesafe.ai](https://console.typesafe.ai) in your browser.
2. Use a secure, short-lived shell environment to export your cookie string:
   ```bash
   export TYPESAFE_CONSOLE_COOKIE="your-cookie-string"
   ```

**Option B — agentcookie (automatic):**
If you use [agentcookie](https://github.com/nichochar/agentcookie) to access your own browser sessions, the CLI can read the current `typesafe.ai` cookies automatically:
```bash
# No manual setup needed — just be signed in to console.typesafe.ai in Chrome
typesafe-keys list
```

---

## Usage

### List all keys

```bash
typesafe-keys list
```

```
NAME                         STATUS     KEY (REDACTED)             CREATED              ID
-------------------------------------------------------------------------------------------------------------------
Example Application          Active     <redacted>                  2026-01-15           key_example_1
Staging Project              Active     <redacted>                  2026-02-01           key_example_2
```

### Create a key

```bash
typesafe-keys create "My Project Name"
```

```
Successfully created TypeSafe API key: 'My Project Name'
Key ID:  key_example_3
API Key: <shown once — store it securely>
```

Options:
```bash
# Copy the new key to clipboard (macOS)
typesafe-keys create "My Key" --copy

# Non-interactive key creation (explicit confirmation required)
typesafe-keys create "My Key" --yes

# Machine-readable output
typesafe-keys create "My Key" --json
```

### Activate / Deactivate a key

```bash
typesafe-keys activate key_abc123
typesafe-keys deactivate key_abc123
```

### Delete a key

```bash
typesafe-keys delete key_abc123

# Use --yes for scripts and other non-interactive sessions
typesafe-keys delete key_abc123 --yes
```

### JSON output

All commands support `--json` for machine-readable output:

```bash
typesafe-keys list --json
```

---

## Using your API key

Once you have a key, set it as an environment variable:

```bash
export TYPESAFE_API_KEY="<your-api-key>"
```

Then use it with the [TypeSafe Python SDK](https://docs.typesafe.ai/sdk/python):

```python
from typesafe_ai import TypeSafeClient, Choice

client = TypeSafeClient()  # reads TYPESAFE_API_KEY from env

result = client.ask(
    state="The user said: 'Cancel my subscription immediately'",
    questions=[
        Choice(
            question="What is the user's intent?",
            options=["cancel", "downgrade", "complaint", "question"],
        ),
    ],
)

print(result.answers[0].choice)        # "cancel"
print(result.answers[0].confidence)    # 0.97
print(result.answers[0].probabilities) # {"cancel": 0.94, "complaint": 0.04, ...}
```

Or with the [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript):

```javascript
import { TypeSafeClient, choice } from '@typesafe-ai/client';

const client = new TypeSafeClient();

const result = await client.ask({
  state: 'The user said: "Cancel my subscription immediately"',
  questions: [
    choice({
      question: "What is the user's intent?",
      options: ["cancel", "downgrade", "complaint", "question"],
    }),
  ],
});

console.log(result.answers[0].choice);     // "cancel"
console.log(result.answers[0].confidence); // 0.97
```

---

## License

MIT

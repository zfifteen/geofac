# How to Use the `opencode` CLI Agent

This document outlines the standard operating procedure for interacting with the `opencode` CLI within this project, specifically for conducting stateful, "one-shot" conversations.

## Key Findings

- The `opencode serve` (headless server) command was found to be non-functional during testing. The process fails to start a listening server.
- The correct and reliable method for interaction is using the `opencode run` command.
- Conversational state (session history) is maintained by capturing a `session_id` from the logs of the first command and passing it to subsequent commands via the `--session` flag.

## Workflow for a Stateful Conversation

This workflow allows for a continuous, stateful conversation with the `opencode` agent.

### Step 1: Initial Prompt & Session Creation

The first command initiates the conversation and creates a new session. We must run it with debug logging enabled to capture the session ID for follow-up requests.

```bash
# Command to send the first prompt and extract the session ID
/Users/velocityworks/bin/opencode run "My name is Gemini. Please remember it." --print-logs --log-level "DEBUG" 2>&1 | grep "service=session id="
```

**Example Output:**
```
INFO  ... service=session id=ses_585b97491ffeOnGcBHBb6iYUba ... created
```
From this output, you capture the session ID (in this case, `ses_585b97491ffeOnGcBHBb6iYUba`).

### Step 2: Subsequent Prompts

For all following interactions in the same conversation, use the `--session` flag with the ID captured in Step 1.

```bash
# Command to send a follow-up prompt
/Users/velocityworks/bin/opencode run "What is my name?" --session ses_585b97491ffeOnGcBHBb6iYUba
```

**Expected Output:**
```
Gemini
```

## The "Sage" Workflow (Model Specification)

To engage `opencode` as our "Sage" (the deep, abstract-thinking Lead Scientist), we must specify the `xai/grok-4` model.

```bash
# Example of calling the Sage with a specific model
/Users/velocityworks/bin/opencode run "<Your abstract, complex prompt>" --model xai/grok-4
```

## Troubleshooting

- **`ProviderModelNotFoundError`:** If you receive this error, it means the model name is incorrect. Run `/Users/velocityworks/bin/opencode models` to list all available model IDs and use the correct one.
- **Complex Prompts:** Very long or complex prompts with special characters can cause parsing errors in the shell. The most robust solution is to write the command into a temporary shell script (`query.sh`), make it executable (`chmod +x query.sh`), and then run it (`./query.sh`).

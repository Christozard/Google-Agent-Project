"""
agent.py — a minimal autonomous coding agent powered by a local Ollama model.

WHAT THIS DOES
---------------
This gives the model three "tools" it can call:
  - read_file(path)              -> read a file's contents
  - write_file(path, content)    -> create/overwrite a file
  - run_command(command)         -> run a shell command (npm install, mkdir, etc.)

The model is given your plan.md and told to start implementing it. It responds
with either plain text, or a request to call one of the tools above. This
script executes that tool call, feeds the result back to the model, and
repeats — that's the entire "agent loop". It keeps going until the model
stops asking for tool calls (i.e. it thinks it's done, or it's waiting on you).

Every write_file and run_command call is shown to you and requires a y/n
confirmation before it executes (see REQUIRE_CONFIRMATION below). This is
the main thing standing between "agent" and "agent that deletes your repo".
Turn it off only if you know what you're doing.

HOW TO RUN
----------
1. Install the Ollama python client:
     pip install ollama --break-system-packages

2. Make sure Ollama is running and your model is pulled:
     ollama pull qwen2.5-coder:32b

3. Put this script in your project repo root (same folder as plan.md).

4. Run it:
     python agent.py

5. It will prompt you for an initial instruction (or just press Enter to use
   the default "read plan.md and start on Phase 1").

6. From there, watch the terminal output. Whenever it wants to write a file
   or run a command, it'll show you exactly what and ask for confirmation.
   Type 'y' to allow it, 'n' to reject (the model will be told the action was
   denied and can try something else), or 'q' to quit the whole loop.

7. The conversation keeps going in a single session — the model remembers
   everything it's done so far in this run. If you quit and rerun, it starts
   fresh with no memory of the previous run (this script doesn't persist
   conversation history to disk).

CONFIGURATION
-------------
Change MODEL below to whatever you've pulled in Ollama.
Change WORKDIR if you want the agent operating on a different folder than
the one this script lives in.
"""

import json
import os
import re
import subprocess
import sys

import ollama

MODEL = "qwen2.5-coder:14b"
WORKDIR = os.path.dirname(os.path.abspath(__file__))
REQUIRE_CONFIRMATION = True  # set False to let it write/run without asking (not recommended)
MAX_TURNS = 50  # safety cap so a confused model can't loop forever


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file, relative to the project root.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Relative file path"}},
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Create or overwrite a file with the given content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Relative file path"},
                    "content": {"type": "string", "description": "Full file content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Run a shell command in the project root (e.g. 'npm install', 'mkdir src').",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "Shell command to run"}},
                "required": ["command"],
            },
        },
    },
]


def _resolve(path: str) -> str:
    """Keep file operations confined to WORKDIR."""
    full = os.path.abspath(os.path.join(WORKDIR, path))
    if not full.startswith(WORKDIR):
        raise ValueError(f"Refusing to touch path outside project root: {path}")
    return full


def confirm(prompt: str) -> bool:
    if not REQUIRE_CONFIRMATION:
        return True
    resp = input(f"{prompt}\n  Allow? [y/n/q] ").strip().lower()
    if resp == "q":
        print("Quitting.")
        sys.exit(0)
    return resp == "y"


def read_file(path: str) -> str:
    try:
        with open(_resolve(path), "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"ERROR reading {path}: {e}"


def write_file(path: str, content: str) -> str:
    preview = content if len(content) < 500 else content[:500] + "\n... (truncated in preview)"
    print(f"\n--- proposed write to {path} ---\n{preview}\n---")
    if not confirm(f"Write file: {path} ({len(content)} chars)"):
        return "DENIED by user."
    try:
        full = _resolve(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Wrote {path} successfully."
    except Exception as e:
        return f"ERROR writing {path}: {e}"


def run_command(command: str) -> str:
    if not confirm(f"Run command: {command}"):
        return "DENIED by user."
    try:
        result = subprocess.run(
            command, shell=True, cwd=WORKDIR, capture_output=True, text=True, timeout=120
        )
        output = (result.stdout or "") + (result.stderr or "")
        return output[:3000] if output else f"Command exited with code {result.returncode}, no output."
    except Exception as e:
        return f"ERROR running command: {e}"


DISPATCH = {"read_file": read_file, "write_file": write_file, "run_command": run_command}

TOOL_NAMES = set(DISPATCH.keys())


def extract_fallback_tool_call(content: str):
    """
    Some Ollama models (qwen2.5-coder especially) don't populate the proper
    structured tool_calls field and instead print one or more tool calls as
    raw JSON text in content — sometimes several back-to-back, sometimes with
    trailing shell-style '# comment' text inside a field, which breaks
    json.loads. This scans content for each individual {...} block, strips
    trailing '# ...' comments per line, and parses them independently.
    Returns a list of (name, args_dict) tuples, possibly empty.
    """
    if not content:
        return []

    results = []
    depth = 0
    start = None
    for i, ch in enumerate(content):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            if depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    raw = content[start:i + 1]
                    # strip trailing "# ..." comments that can appear after a
                    # quoted value on the same line, e.g. "...activate"  # macOS
                    cleaned = re.sub(r'"\s*#[^\n"]*', '"', raw)
                    try:
                        data = json.loads(cleaned)
                    except json.JSONDecodeError:
                        continue
                    name = data.get("name")
                    args = data.get("arguments")
                    if name in TOOL_NAMES and isinstance(args, dict):
                        results.append((name, args))
    return results

def main():
    print(f"Agent starting. Model: {MODEL}. Working dir: {WORKDIR}\n")
    task = input("Initial instruction (Enter for default): ").strip()
    if not task:
        task = "Read plan.md and start implementing Phase 1. Ask before doing anything destructive."

    messages = [{"role": "user", "content": task}]

    for turn in range(MAX_TURNS):
        response = ollama.chat(model=MODEL, messages=messages, tools=TOOLS)
        msg = response["message"]
        messages.append(msg)

        tool_calls = msg.get("tool_calls")

        if not tool_calls:
            fallback_calls = extract_fallback_tool_call(msg.get("content", ""))
            if fallback_calls:
                for name, args in fallback_calls:
                    print(f"[tool call, fallback-parsed from content] {name}({args})")
                    fn = DISPATCH.get(name)
                    result = fn(**args) if fn else f"Unknown tool: {name}"
                    messages.append({"role": "user", "content": f"Tool result for {name}: {result}"})
                continue

            if msg.get("content"):
                print(f"\n[model]: {msg['content']}\n")
            followup = input("Model has no further tool calls. Reply (or Enter to stop): ").strip()
            if not followup:
                break
            messages.append({"role": "user", "content": followup})
            continue

        if msg.get("content"):
            print(f"\n[model]: {msg['content']}\n")

        for call in tool_calls:
            name = call["function"]["name"]
            args = call["function"]["arguments"]
            print(f"[tool call] {name}({args})")
            fn = DISPATCH.get(name)
            result = fn(**args) if fn else f"Unknown tool: {name}"
            messages.append({"role": "tool", "content": str(result)})
    else:
        print(f"\nHit MAX_TURNS ({MAX_TURNS}). Stopping to avoid a runaway loop.")

    print("\nDone.")


if __name__ == "__main__":
    main()
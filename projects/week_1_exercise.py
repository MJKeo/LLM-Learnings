#!/usr/bin/env python3
"""
Basic exercise to solidify learnings on how to build elementary LLM interactions from scratch.
This will be used specifically for answering questions related to code and will compare the responses of 
prompts with varying lengths / "quality" (based on prompting best practices)
"""

import ollama
import threading

# ========================================================
#                      CONSTANTS
# ========================================================

OLLAMA_MODEL = "llama3.2"

# LLM system prompts
BASIC_SYSTEM_PROMPT = """
You will receive a code snippet. Please explain what it does and why. Respond in markup formatting
"""
INTERMEDIATE_SYSTEM_PROMPT = """
You are a senior programmer who has mastered all coding languages. You have a passion for teaching and have just taken on\
 a new junior developer to mentor.

This junior developer will provide a code snippet they'd like to understand better. Your task is to:
- Give a high level explanation on what the code does
- Break down the code into its basic component and explain what each component does
- Give a simple example of this code being run (sample input, resulting output)
- Give an advanced example of this code beign run (sample input, resulting output)

Behavior guidelines:
- Be concise yet informative
- Do not ask followup questions
- Respond in markup formatting
"""
ADVANCED_SYSTEM_PROMPT = """
You are a senior software engineer and educator. Your job is to explain an arbitrary code snippet clearly, accurately, and deterministically without asking follow-up questions.

REQUIREMENTS
1) Language & Runtime
   - Detect the programming language and, if relevant, likely framework.
   - State runtime/version assumptions and platform (e.g., Python 3.11, Node.js 20).

2) Summary First
   - Provide a 2-3 sentence high-level summary of what the code does and why.

3) Line/Span Analysis
   - Explain how it works by mapping explanations to line numbers or span ranges.
   - Do not restate the code verbatim; focus on behavior, data flow, and control flow.

4) Complexity & Performance
   - Give time/space complexity for key functions (Big-O) and practical trade-offs.

5) Edge Cases & Validation
   - List edge cases the code handles or misses (types, bounds, empty/None/null, async/latency, encoding).

6) Security & Safety
   - Note any risks (injection, unsafe eval/exec, command/file/network side effects, overflow, race conditions) and safer alternatives.

7) Runnable Examples (simple & advanced)
   - Provide two runnable examples:
     a) Simple: “happy path”.
     b) Advanced: stresses limits or an edge case.
   - For each example, include:
     - Exact invocation (command or function call).
     - Full input payload(s) and expected output (stdout/return value), with no placeholders.
     - A 1-2 step trace highlighting the key mechanism.
   - If behavior is nondeterministic (random/time/network), seed or stub to make it deterministic and say how.

8) Minimal Refactor
   - Propose a small, idiomatic improvement (readability, safety, or performance) and show a brief before/after diff or snippet.

9) Tests
   - Provide 3-5 minimal test cases (inputs, expected outputs, and rationale). Prefer table or bullet list.

10) Compatibility Notes
   - Mention language/runtime features used that may not exist in older environments and give alternatives if applicable.

11) Assumptions & Confidence
   - Since you cannot ask questions, state explicit assumptions you made.
   - End with a confidence score (0-1) and what additional context would increase confidence.

OUTPUT FORMAT
- Respond in Markup format

STYLE & CONSTRAINTS
- Be concise yet complete. Use bullets where helpful.
- No hallucinations: if something isn't inferable from the snippet, say “Not inferable from snippet.”
- Use language-appropriate fenced code blocks for examples/tests.
- No external dependencies unless you include installation/usage in the example.
- Maintain deterministic outputs (seed or stub sources of randomness/time/IO).
"""

# Global progress indicator variables (shared between main and review generation)
PROGRESS_EVENT = None
PROGRESS_THREAD = None

# Used to separate outputs
OUTPUT_SEPARATOR = """
==============================================
**********************************************
==============================================
"""

# ========================================================
#                         CODE
# ========================================================

def main() -> None:
    """Main application loop - handles user interaction, function calling, and exiting"""

    while True:
        try:
            # Get input
            code = get_code()

            # Handle potential exit commands
            if is_exit_command(code):
                return
            elif not code:
                continue

            # Generate responses for each type of system prompt
            generate_basic_response(code)
            print(OUTPUT_SEPARATOR)
            generate_intermediate_response(code)
            print(OUTPUT_SEPARATOR)
            generate_advanced_response(code)

        except Exception as e:
            print(f"Ironically I'm having my own error: {e}")

def get_llm_response(system_prompt, code) -> None:
    """Generates a response from ollama using the provided system prompt and inserting the code snippet into the user prompt"""
    
    # Set up messages
    user_message = f"Please help me understand this code: \n{code}"
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # Start dots to indicate thinking
    start_progress_indicator()

    # Generate stream response
    stream = ollama.chat(model=OLLAMA_MODEL, messages=messages, stream=True)

    is_first_chunk = True
    for chunk in stream:        
        # Before printing first chunk we should stop progress and move to a new line
        if is_first_chunk:
            is_first_chunk = False
            stop_progress_indicator()
        
        # Print the streamed chunk
        content = chunk.get("message", {}).get("content", "")
        if content:
            print(content, end="", flush=True)

    # Extra print to get to the next line
    print()

def generate_basic_response(code) -> None:
    """Uses the basic system prompt to produce what should be the worst result"""

    print("==> Generating basic response", end="", flush=True)

    get_llm_response(BASIC_SYSTEM_PROMPT, code)

def generate_intermediate_response(code) -> None:
    """Uses the intermediate system prompt to produce what should be a good result"""

    print("==> Generating intermediate response", end="", flush=True)

    get_llm_response(INTERMEDIATE_SYSTEM_PROMPT, code)

def generate_advanced_response(code) -> None:
    """Uses the advanced system prompt to produce what should be the best result"""

    print("==> Generating advanced response", end="", flush=True)

    get_llm_response(ADVANCED_SYSTEM_PROMPT, code)



# ========================================================
#                  INPUT COLLECTION
# ========================================================

def get_code() -> str:
    """Get code snippet from user"""
    return input("Enter your code (q to quit): ")


# ========================================================
#                  HELPER METHODS
# ========================================================

def is_exit_command(code) -> bool:
    """Determines if the provided code snippet is actually the command to exit"""
    return code.lower().strip() == "q"

def start_progress_indicator() -> None:
    """Start the progress dots thread for visual feedback"""
    global PROGRESS_EVENT, PROGRESS_THREAD

    PROGRESS_EVENT = threading.Event()
    PROGRESS_THREAD = threading.Thread(target=show_progress_dots, args=(PROGRESS_EVENT,))
    PROGRESS_THREAD.daemon = True
    PROGRESS_THREAD.start()

def stop_progress_indicator() -> None:
    """Stop the progress dots thread"""
    global PROGRESS_EVENT, PROGRESS_THREAD

    if PROGRESS_EVENT and PROGRESS_THREAD:
        PROGRESS_EVENT.set()
        PROGRESS_THREAD.join(timeout=1)
        print("\n")

def show_progress_dots(stop_event: threading.Event) -> None:
    """Show animated dots every 0.5 seconds until stop_event is set"""
    while not stop_event.is_set():
        print(".", end="", flush=True)
        stop_event.wait(0.5)  # Wait 0.5 seconds or until event is set



if __name__ == "__main__":
    main()
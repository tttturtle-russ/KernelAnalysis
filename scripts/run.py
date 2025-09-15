import os
import argparse
import json
import sys
from llm import LLM
from tool import TOOLSET
from prompt import SYSTEM_PROMPT_TEMPLATE, USER_PROMPT_START_TEMPLATE, USER_PROMPT_END_TEMPLATE

MAX_TOKENS = 1024 * 128
# should be 0.3, but 0.6 is safer
CHAR_PER_TOKEN = 0.6

def estimate_tokens(text):
    return len(text) * CHAR_PER_TOKEN

def minify_json_string(json_string):
    """
    Minifies a JSON string for minimal token usage.
    """
    obj = json.loads(json_string)
    return json.dumps(obj, separators=(',', ':'))

def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input", type=str, help="Path to the control flow path JSON file.")
    argparser.add_argument("--output", type=str, help="Path to save the final result JSON file.")
    args = argparser.parse_args()
    input = args.input
    output = args.output
    with open(input, "r") as f:
        path_data = json.load(f)

    func1 = path_data["func1"]
    func2 = path_data["func2"]
    driver = path_data["driver"]
    path = path_data["path"]
    paths = json.dumps(path)

    SYSTEM_PROMPT = SYSTEM_PROMPT_TEMPLATE.format(
        TOOLSET=json.dumps(TOOLSET),
        FUNC1=func1,
        FUNC2=func2,
        DRIVER=driver
    )

    USER_PROMPT = f"{USER_PROMPT_START_TEMPLATE}\n```json\n{minify_json_string(paths)}\n```{USER_PROMPT_END_TEMPLATE}"
    if estimate_tokens(USER_PROMPT) > MAX_TOKENS:
        USER_PROMPT = [f"```json\n{json.dumps({func: paths})}```" for func, paths in path.items()]
        USER_PROMPT[0] = USER_PROMPT_START_TEMPLATE + USER_PROMPT[0]
        USER_PROMPT[-1] = USER_PROMPT[-1] + "\n" + USER_PROMPT_END_TEMPLATE

    agent = LLM(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_KEY"),
        base_url="https://api.deepseek.com",
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT,
        toolset=TOOLSET,
    )
    try:
        agent.run()
    finally:
        agent.shutdown(output)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
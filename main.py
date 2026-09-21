import agent

def extract_text(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        )
    return str(content)

def run():

    analyzer = agent.init_agent()
    thread_config = {"configurable": {"thread_id": "1"}}


    print("Chat started. Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        result = analyzer.invoke(
            {"messages": [{"role": "user", "content": user_input}]},
            thread_config,
        )

        response = extract_text(result["messages"][-1].content)
        print(f"\nAssistant: {response}\n")

run()
    

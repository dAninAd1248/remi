from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from tools.get_meals_for_recipe import search_meal_by_name

from dotenv import load_dotenv
import os

## Helper Function to stream updates from the graph
from langchain_core.messages import convert_to_messages
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def pretty_print_message(message, indent=False):
    pretty_message = message.pretty_repr(html=True)
    if not indent:
        print(pretty_message)
        return

    indented = "\n".join("\t" + c for c in pretty_message.split("\n"))
    print(indented)


def pretty_print_messages(update, last_message=False):
    is_subgraph = False
    if isinstance(update, tuple):
        ns, update = update
        # skip parent graph updates in the printouts
        if len(ns) == 0:
            return

        graph_id = ns[-1].split(":")[0]
        print(f"Update from subgraph {graph_id}:")
        print("\n")
        is_subgraph = True

    for node_name, node_update in update.items():
        update_label = f"Update from node {node_name}:"
        if is_subgraph:
            update_label = "\t" + update_label

        print(update_label)
        print("\n")

        messages = convert_to_messages(node_update["messages"])
        if last_message:
            messages = messages[-1:]

        for m in messages:
            pretty_print_message(m, indent=is_subgraph)
        print("\n")




main_ingredient_agent = create_react_agent(
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.0),
    #model = ChatOpenAI(model="gpt-5"),
    tools=[search_meal_by_name],
    prompt=(
        "You are a main ingredient agent.\n\n"
        "INSTRUCTIONS:\n"
        "This tool goal is tool is to find a meal with a random ingredient given by the user."
        "If ingredient not in english translate to english. "
        "If the ingredient has spaces, replace the space with an underscore. "
        "- Assist ONLY with research-related tasks, DO NOT do any math\n"
        "- After you're done with your tasks, respond to the supervisor directly\n"
        "- Respond ONLY with the results of your work, do NOT include ANY other text."),name="main_ingredient_agent",)

input = "I want a recipe for fettucine alfredo"
for chunk in main_ingredient_agent.stream({"messages": [{"role": "user", "content": input}]}):
    pretty_print_messages(chunk)



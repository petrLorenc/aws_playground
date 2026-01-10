from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from langchain.agents import create_agent
from neo4j import Driver, RoutingControl
from neo4j_graphrag.schema import get_schema

from database.cypher_agent.prompts import CYPHER_GENERATION_PROMPT, CYPHER_QA_PROMPT

SYSTEM_PROMPT = """You are a helpful assistant that answers questions using a Neo4j Graph Database.

Use the available tools to retrieve information from the database and provide accurate answers.
Limit answer to 5 results maximum. Only focus on the names of activities.
Always answer in Czech language."""


def get_agent(llm: BaseChatModel, driver: Driver):
    """Create a Cypher agent using LangGraph."""

    @tool
    def run_cypher_query(cypher_query: str) -> str:
        """Run a Cypher query against the Neo4j database and return results. Always generate a Cypher query before calling this tool.

        Args:
            cypher_query: The Cypher query string to execute
        """
        try:
            result = driver.execute_query(
                cypher_query, database_="neo4j", routing_control=RoutingControl.READ
            )
            records = [record.data() for record in result.records]
            if not records:
                return "No results found."
            return str(records)
        except Exception as e:
            return f"Error executing Cypher query: {e}"

    @tool
    def generate_cypher(question: str, database_schema: str) -> str:
        """Generate a Cypher query based on the user question and database schema.

        Args:
            question: The user's question in natural language
            database_schema: The Neo4j database schema
        """
        chain = CYPHER_GENERATION_PROMPT | llm | StrOutputParser()
        return chain.invoke({"schema": database_schema, "question": question})

    @tool
    def get_schema_neo4j() -> str:
        """Retrieve the Neo4j database schema including node labels, relationship types, and properties."""
        try:
            schema = get_schema(driver)
            return schema
        except Exception as e:
            return f"Error retrieving schema: {e}"

    @tool
    def answer_question(context: str, question: str) -> str:
        """Generate a human-understandable answer based on the database context and original question. Usually as last step before returning the final answer. This is usually the final answer.

        Args:
            context: The data retrieved from the database
            question: The original user question
        """
        chain = CYPHER_QA_PROMPT | llm | StrOutputParser()
        return chain.invoke({"context": context, "question": question})

    tools = [run_cypher_query, generate_cypher, get_schema_neo4j, answer_question]

    # Create an agent using LangChain
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        debug=True,
    )
    return agent


if __name__ == "__main__":
    from langchain_openai import AzureChatOpenAI
    from neo4j import GraphDatabase
    from pydantic import SecretStr
    import os
    from dotenv import load_dotenv

    load_dotenv()

    driver = GraphDatabase.driver(
        os.getenv("GRAPH_DATABASE_URI", "bolt://localhost:7687"),
        auth=(
            os.getenv("GRAPH_DATABASE_USERNAME", ""),
            os.getenv("GRAPH_DATABASE_PASSWORD", ""),
        ),
    )

    llm = AzureChatOpenAI(
        openai_api_type="azure",
        azure_endpoint=os.getenv("API_BASE_URL"),
        api_version="2024-10-21",
        api_key=SecretStr(secret_value=os.getenv("API_KEY", "")),
        azure_deployment="gpt-5-mini-2025-08-07",
    )

    agent = get_agent(llm, driver)

    # Example usage - invoke with messages format for LangGraph
    question = "Najdi mi všechny aktivity spojené s programováním na Vysočině."

    # LangGraph agents expect messages format
    response = agent.invoke({"messages": [HumanMessage(content=question)]})

    # Extract the final response
    print("Agent response:")
    for message in response["messages"]:
        if hasattr(message, "content") and message.content:
            print(f"  [{message.__class__.__name__}]: {message.content[:500]}...")
        else:
            print(f"  [{message.__class__.__name__}]: <no content>")

    # Print final answer
    final_message = response["messages"][-1]
    print("\n--- Final Answer ---")
    print(final_message.content)

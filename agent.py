from agents import Agent, Runner , AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()

set_tracing_disabled(True)


async def llm_agent(input_text: str, MODEL: str = "gemini-2.0-flash") -> str:
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    

    model = OpenAIChatCompletionsModel(
        openai_client=external_client,
        model=MODEL,
    )  
    agent = Agent(name="LLM Agent", instructions="You are a helpful assistant.", model=model)
    result = await Runner.run(starting_agent=agent, input=input_text)
    # print(f"result.raw_responses: {result.raw_responses}\n")
    # print(f"result.final_output: {result.new_items}\n")
    return result.final_output


result = asyncio.run(llm_agent("Write a poem about the sea.in three lines"))
from agents import Agent, Runner , AsyncOpenAI , OpenAIChatCompletionsModel , set_tracing_disabled
import asyncio
from dotenv import load_dotenv
import os
load_dotenv()



async def llm_agent(input_text: str):
    external_client = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    

    model = OpenAIChatCompletionsModel(
        openai_client=external_client,
        model="gemini-2.0-flash",
    )  
    agent = Agent(name="LLM Agent", instructions="You are a helpful assistant.", model=model)
    result = await Runner.run(starting_agent=agent, input=input_text)
    # print(result.final_output)
    return result.final_output


# result = asyncio.run(llm_agent("Write a poem about the sea."))
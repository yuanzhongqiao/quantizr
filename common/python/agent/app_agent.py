"""This is the main agent module that scans the source code and generates the AI prompt."""

import os
import sys
import time
from typing import List
from gradio import ChatMessage
from langchain.schema import HumanMessage, SystemMessage, AIMessage, BaseMessage
from langchain.chat_models.base import BaseChatModel
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import BaseTool

from ..utils import RefactorMode
from ..file_utils import FileUtils
from ..utils import RefactorMode
from .prompt_utils import PromptUtils

ABS_FILE = os.path.abspath(__file__)
PRJ_DIR = os.path.dirname(os.path.dirname(ABS_FILE))
sys.path.append(PRJ_DIR)

from common.python.agent.models import FileSources
from common.python.agent.ai_utils import AIUtils, init_tools

class QuantaAgent:
    """Scans the source code and generates the AI prompt."""

    # I'm not sure it's best practice or not, but for now I'll only create tools once and store here
    tool_set: List[BaseTool] | None = None

    def __init__(self):
        self.ts: str = str(int(time.time() * 1000))
        self.answer: str = ""
        self.mode = RefactorMode.NONE.value
        self.prompt: str = ""
        self.prompt_code: str = ""
        self.system_prompt: str = ""
        self.file_sources: FileSources
        self.dry_run: bool = False
    
    def run(
        self,
        user_system_prompt: str,
        ai_service: str,
        mode: str,
        output_file_name: str,
        messages: List[BaseMessage],
        input_prompt: str,
        file_sources: FileSources,
        llm: BaseChatModel
    ):
        """Runs the AI/Agent when called from the Quanta Web app
        """
        self.file_sources = file_sources
        self.prompt = input_prompt
        self.mode = mode

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts
        
        if (self.prompt_code): 
            self.prompt += "\n<code>\n" + self.prompt_code + "\n</code>\n"

        self.system_prompt = self.build_system_prompt(user_system_prompt)

        if self.dry_run:
            # If dry_run is True, we simulate the AI response by reading from a file
            # if we canfind that file or else we return a default response.
            answer_file: str = f"{self.file_sources.data_folder}/dry-run-answer.txt"

            if os.path.isfile(answer_file):
                print(f"Simulating AI Response by reading answer from {answer_file}")
                self.answer = FileUtils.read_file(answer_file)
            else:
                self.answer = "Dry Run: No API call made."
        else:
            # Check the first 'message' to see if it's a SystemMessage and if not then insert one
            if len(messages) == 0 or not isinstance(messages[0], SystemMessage):
                messages.insert(0, SystemMessage(content=self.system_prompt))
            # else we set the first message to the system prompt
            else:
                messages[0] = SystemMessage(content=self.system_prompt)

            self.human_message = HumanMessage(content=self.prompt)
            messages.append(self.human_message)
            use_tools = True

            if use_tools and self.mode != RefactorMode.NONE.value:
                tools = []
                if self.mode == RefactorMode.REFACTOR.value:
                    if QuantaAgent.tool_set is None:
                        QuantaAgent.tool_set = init_tools(self.file_sources)
                    tools = QuantaAgent.tool_set
                    print("Created Agent Tools")
                    
                agent = create_react_agent(
                    model=llm,
                    tools=tools,
                )
                
                initial_message_len = len(messages)
                response = agent.invoke({"messages": messages})
                # print(f"Response: {response}") This prints too much
                resp_messages = response["messages"]
                new_messages = resp_messages[initial_message_len:]
                self.answer = ""
                resp_idx: int = 0
                
                # Scan all the new messages for AI responses, which may contain tool calls
                for message in new_messages:
                    if isinstance(message, AIMessage):
                        resp_idx += 1
                        # print(f"AI Response {resp_idx}:")
                        # pprint.pprint(message)
                        self.answer = self.append_message(message, self.answer)
                           
                # Agents may add multiple new messages, so we need to update the messages list
                # This [:] syntax is a way to update the list in place
                messages[:] = resp_messages
            else:
                print("Running without tools")
                response = llm.invoke(messages)
                self.answer = response.content  # type: ignore
                messages.append(AIMessage(content=response.content))

        output = f"""AI Model Used: {ai_service}, Mode: {self.mode}, Timestamp: {self.ts}
____________________________________________________________________________________
Input Prompt: 
{input_prompt}
____________________________________________________________________________________
LLM Output: 
{self.answer}
____________________________________________________________________________________
System Prompt: 
{self.system_prompt}
____________________________________________________________________________________
Final Prompt: 
{self.prompt}
"""

        filename = f"{self.file_sources.data_folder}/{output_file_name}.txt"
        FileUtils.write_file(filename, output)
        print(f"Wrote Log File: {filename}")

    async def run_gradio(
        self,
        ai_service: str,
        output_file_name: str,
        messages,
        show_tool_usage: bool, 
        input_prompt: str,
        file_sources: FileSources,
        llm: BaseChatModel,
    ):
        """Runs the AI/Agent from a Gradio UI.
        """
        self.file_sources = file_sources
        self.prompt = input_prompt
        self.mode = RefactorMode.REFACTOR.value

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts
        
        self.system_prompt = self.build_system_prompt("")
        
        if QuantaAgent.tool_set is None:
            QuantaAgent.tool_set = init_tools(self.file_sources)
                
        # Convert messages to a format the agent can understand 
        chat_history = AIUtils.gradio_messages_to_langchain(messages) 

        agent = create_react_agent(
            model=llm,
            tools=QuantaAgent.tool_set,
        )
        chat_history.append(HumanMessage(content=self.prompt))    
        messages.append(ChatMessage(role="user", content=self.prompt))
        yield messages
        
        print("Processing agent responses...")
        async for chunk in agent.astream({"messages": chat_history}):
            AIUtils.handle_agent_response_item(chunk, messages, show_tool_usage)
            yield messages            
            
        output = f"""AI Model Used: {ai_service}, Mode: {self.mode}, Timestamp: {self.ts}
____________________________________________________________________________________
Input Prompt: 
{input_prompt}
____________________________________________________________________________________
LLM Output: 
{self.answer}
____________________________________________________________________________________
System Prompt: 
{self.system_prompt}
____________________________________________________________________________________
Final Prompt: 
{self.prompt}
"""

        filename = f"{self.file_sources.data_folder}/{output_file_name}.txt"
        FileUtils.write_file(filename, output)
        print(f"Wrote Log File: {filename}")

    def append_message(self, message: AIMessage, answer: str) -> str:
        if isinstance(message.content, str):
            answer += message.content + "\n"
        else:
            if isinstance(message.content, list): 
                # if message.content is a list
                for item in message.content:
                    if isinstance(item, dict) and "type" in item and item["type"] == "tool_use":
                        answer += "Tool Used: " + item["name"] + "\n"
                    elif isinstance(item, dict) and "text" in item:
                        answer += item["text"] + "\n"
                    else:
                        answer += str(item) + "\n"
        return answer

    async def run_lang_graph(
        self,
        verbatim_system_prompt: str,
        ai_service: str,
        output_file_name: str,
        messages,
        show_tool_usage: bool, 
        input_prompt: str,
        file_sources: FileSources,
        graph,
    ):
        """Runs the AI/Agent from a Gradio UI.
        """
        
        self.file_sources = file_sources
        self.prompt = input_prompt
        self.mode = RefactorMode.REFACTOR.value

        # default filename to timestamp if empty
        if output_file_name == "":
            output_file_name = self.ts
        
        if verbatim_system_prompt:
            self.system_prompt = verbatim_system_prompt
        else:
            self.system_prompt = self.build_system_prompt("")
                
        # Convert messages to a format the agent can understand
        chat_history = AIUtils.gradio_messages_to_langchain(messages) 

        chat_history.append(HumanMessage(content=self.prompt))    
        chat_history.insert(0, SystemMessage(content=self.system_prompt))
        
        messages.append(ChatMessage(role="user", content=self.prompt))
        yield messages     
        
        print("Processing agent responses...")
        async for chunk in graph.astream({"messages": chat_history}):
            AIUtils.handle_agent_response_item(chunk, messages, show_tool_usage)
            yield messages       
            
        output = f"""AI Model Used: {ai_service}, Mode: {self.mode}, Timestamp: {self.ts}
____________________________________________________________________________________
Input Prompt: 
{input_prompt}
____________________________________________________________________________________
LLM Output: 
{self.answer}
____________________________________________________________________________________
System Prompt: 
{self.system_prompt}
____________________________________________________________________________________
Final Prompt: 
{self.prompt}
"""

        filename = f"{self.file_sources.data_folder}/{output_file_name}.txt"
        FileUtils.write_file(filename, output)
        print(f"Wrote Log File: {filename}")

    def get_file_type_mention(self, ext: str) -> str:
        file_type = ""
        if ext == ".py":
            file_type = "Python"
        elif ext == ".js":
            file_type = "JavaScript"
        elif ext == ".html":
            file_type = "HTML"
        elif ext == ".css":
            file_type = "CSS"
        elif ext == ".json":
            file_type = "JSON"
        elif ext == ".txt":
            file_type = "Text"
        elif ext == ".md":
            file_type = "Markdown"
        elif ext == ".java":
            file_type = "Java"
        
        if file_type:
            return f"\nI'm working in a {file_type} file. "
        return ""

    def build_system_prompt(self, user_system_prompt: str):
        """Adds all the instructions to the prompt. This includes instructions for inserting blocks, files,
        folders, and creating files.

        WARNING: This method modifies the `prompt` member of the class to have already been configured, and
        also really everything else that this class sets up, so this method should be called last, just before
        the AI query is made.
        """

        system_prompt = PromptUtils.get_template(
            "../common/python/agent/prompt_templates/agent_system_prompt.md"
        )
        
        # Users themselves may have provided a system prompt so add that if so.
        if user_system_prompt:
            system_prompt += f"\n----\nGeneral Instructions:\n{user_system_prompt}"
            
        return system_prompt


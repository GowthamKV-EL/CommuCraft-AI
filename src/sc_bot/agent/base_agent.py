"""
LangChain ReAct Agent for CommuCraft-AI.

This module sets up the main AI agent using LangChain with Google Gemini API,
implementing the ReAct (Reasoning + Acting) pattern for intelligent task execution.

Args:
    None

Returns:
    None

Errors:
    Exception: If agent initialization fails.
"""

import json
import logging
from typing import Any, Optional

from langchain.agents import Tool, create_react_agent
from langchain.prompts import PromptTemplate
from langchain.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI

from sc_bot.config import settings
from sc_bot.storage.json_storage import JSONStorage
from sc_bot.tasks.daily_learning import DailyLearningTask
from sc_bot.tasks.meeting_prep import MeetingPrepTask
from sc_bot.tasks.message_rewriter import MessageRewriterTask
from sc_bot.utils.google_tts import GoogleTextToSpeech

logger = logging.getLogger(__name__)


class CommuCraftAgent:
    """
    Main AI Agent for CommuCraft using LangChain ReAct pattern.

    This agent orchestrates all communication improvement tasks including
    daily learning, message rewriting, and meeting preparation.

    Args:
        None

    Returns:
        None

    Errors:
        Exception: If initialization fails.
    """

    def __init__(self) -> None:
        """
        Initialize CommuCraft Agent with all components.

        Args:
            None

        Returns:
            None

        Errors:
            Exception: If LLM or storage initialization fails.
        """
        try:
            # Initialize LLM
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-pro",
                google_api_key=settings.google_api_key,
                temperature=0.7,
                convert_system_message_to_human=True,
            )

            # Initialize storage
            self.storage = JSONStorage()

            # Initialize TTS
            self.tts = GoogleTextToSpeech()

            # Initialize tasks
            self.daily_learning_task = DailyLearningTask(self.llm, self.storage, self.tts)
            self.message_rewriter_task = MessageRewriterTask(self.llm, self.storage)
            self.meeting_prep_task = MeetingPrepTask(self.llm, self.storage)

            # Setup tools
            self.tools = self._setup_tools()

            # Create agent
            self.agent = self._create_agent()

            logger.info("CommuCraftAgent initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize CommuCraftAgent: {e}")
            raise

    def _setup_tools(self) -> list[Tool]:
        """
        Setup tools for the ReAct agent.

        Args:
            None

        Returns:
            list[Tool]: List of tool definitions.

        Errors:
            Exception: If tool setup fails.

        Example:
            Input: None
            Output: [Tool(...), Tool(...), ...]
        """

        @tool
        def generate_daily_learning() -> str:
            """Generate today's daily learning content with vocabulary and audio pronunciation."""
            try:
                content = self.daily_learning_task.generate_daily_content()
                return json.dumps(
                    {
                        "status": "success",
                        "paragraph": content["paragraph"][:100] + "...",
                        "vocabulary_count": len(content["vocabulary"]),
                        "proficiency": content["proficiency"],
                    }
                )
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})

        @tool
        def rewrite_message(
            message: str, communication_type: str, objective: str, audience: str, tone: str = "professional"
        ) -> str:
            """
            Rewrite a message to improve clarity and professionalism.

            Args:
                message (str): Original message to rewrite.
                communication_type (str): Type (email, chat, document, update).
                objective (str): Goal of the message.
                audience (str): Target audience.
                tone (str): Desired tone (professional, casual, formal, friendly, assertive).

            Returns:
                str: JSON with rewritten message and improvements.

            Errors:
                Exception: If rewriting fails.
            """
            try:
                result = self.message_rewriter_task.rewrite_message(
                    user_id="default_user",
                    message=message,
                    communication_type=communication_type,
                    objective=objective,
                    audience=audience,
                    desired_tone=tone,
                )
                return json.dumps(
                    {
                        "status": "success",
                        "original": result["original"][:50] + "...",
                        "rewritten": result["rewritten"][:100] + "...",
                        "improvements": result["improvements"],
                    }
                )
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})

        @tool
        def prepare_meeting(
            meeting_title: str,
            objective: str,
            audience: str,
            discussion_points: str,
            sensitivities: Optional[str] = None,
        ) -> str:
            """
            Prepare for a meeting or call with talking points and strategies.

            Args:
                meeting_title (str): Title of the meeting.
                objective (str): Primary objective.
                audience (str): Description of participants.
                discussion_points (str): Key points to discuss (comma-separated).
                sensitivities (Optional[str]): Sensitive topics (comma-separated).

            Returns:
                str: JSON with meeting preparation materials.

            Errors:
                Exception: If preparation fails.
            """
            try:
                points = [p.strip() for p in discussion_points.split(",")]
                sens = [s.strip() for s in sensitivities.split(",")] if sensitivities else None

                result = self.meeting_prep_task.prepare_meeting(
                    user_id="default_user",
                    meeting_title=meeting_title,
                    objective=objective,
                    audience=audience,
                    key_discussion_points=points,
                    sensitivities=sens,
                )

                return json.dumps(
                    {
                        "status": "success",
                        "opening": result["opening_statement"][:80] + "...",
                        "talking_points_count": len(result["talking_points"]),
                        "challenging_questions": len(result["challenging_questions"]),
                    }
                )
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})

        @tool
        def get_today_learning() -> str:
            """Retrieve today's daily learning content."""
            try:
                content = self.daily_learning_task.get_today_learning()
                if not content:
                    return json.dumps({"status": "not_found", "message": "No daily learning generated yet"})

                return json.dumps(
                    {
                        "status": "success",
                        "paragraph": content["paragraph"][:100] + "...",
                        "vocabulary_count": len(content["vocabulary"]),
                        "generated_at": content.get("generated_at", ""),
                    }
                )
            except Exception as e:
                return json.dumps({"status": "error", "message": str(e)})

        return [
            Tool(
                name="generate_daily_learning",
                func=generate_daily_learning,
                description="Generate today's daily learning content with vocabulary and audio pronunciation",
            ),
            Tool(
                name="rewrite_message",
                func=rewrite_message,
                description="Rewrite a message to improve clarity and professional tone",
            ),
            Tool(
                name="prepare_meeting",
                func=prepare_meeting,
                description="Prepare for a meeting with talking points, opening statement, and strategies",
            ),
            Tool(
                name="get_today_learning",
                func=get_today_learning,
                description="Get today's already-generated daily learning content",
            ),
        ]

    def _create_agent(self) -> Any:
        """
        Create the ReAct agent.

        Args:
            None

        Returns:
            Any: Configured ReAct agent.

        Errors:
            Exception: If agent creation fails.

        Example:
            Input: None
            Output: ReAct agent instance
        """
        system_prompt = """You are CommuCraft, an AI-powered professional communication coach. 
Your role is to help employees improve their daily communication through:

1. Daily Learning: Generate and deliver daily vocabulary and professional communication insights
2. Message Rewriting: Improve clarity and professionalism of business messages
3. Meeting Preparation: Help prepare for important professional interactions

Guidelines:
- Always preserve the user's original intent while improving clarity
- Tailor communication advice to the user's proficiency level
- Provide actionable, practical suggestions
- Ask for clarification if user intent is unclear (don't guess)
- Be encouraging and supportive in your communication coaching

Available tools:
- generate_daily_learning: Create daily learning content
- rewrite_message: Improve a message
- prepare_meeting: Prepare for meetings/calls
- get_today_learning: Retrieve today's learning

Always explain your recommendations clearly and be ready to answer follow-up questions."""

        prompt_template = PromptTemplate.from_template(
            """You are a professional communication coach. Help the user with their request.

{input}

{agent_scratchpad}"""
        )

        try:
            agent = create_react_agent(self.llm, self.tools, prompt_template)
            logger.info("ReAct agent created successfully")
            return agent
        except Exception as e:
            logger.error(f"Failed to create agent: {e}")
            raise

    def run(self, user_input: str) -> str:
        """
        Run the agent with user input.

        Args:
            user_input (str): User's request or query.

        Returns:
            str: Agent's response.

        Errors:
            Exception: If execution fails.

        Example:
            Input: "Help me rewrite this email: Hello, I need to discuss the project"
            Output: "I'll help you rewrite that email to be more professional..."
        """
        try:
            logger.info(f"Agent processing input: {user_input[:100]}...")
            from langchain.agents import AgentExecutor

            executor = AgentExecutor.from_agent_and_tools(self.agent, self.tools, verbose=True)
            result = executor.invoke({"input": user_input})
            logger.info("Agent execution completed successfully")
            return result.get("output", "Unable to process request")
        except Exception as e:
            logger.error(f"Agent execution failed: {e}")
            raise

    def shutdown(self) -> None:
        """
        Shutdown the agent and cleanup resources.

        Args:
            None

        Returns:
            None

        Errors:
            None
        """
        logger.info("CommuCraftAgent shutdown")

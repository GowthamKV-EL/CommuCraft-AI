"""
Meeting and call preparation task for professional interactions.

This module helps users prepare for meetings and calls by generating talking points,
identifying concerns, and creating preparation checklists.

Args:
    None

Returns:
    None

Errors:
    ValueError: If meeting parameters are invalid.
    Exception: If LLM API calls fail.
"""

import json
import logging
from typing import Any, Optional

from sc_bot.storage.json_storage import JSONStorage

logger = logging.getLogger(__name__)


class MeetingPrepTask:
    """
    Prepare users for meetings and calls with talking points and strategies.

    This class generates comprehensive meeting preparation materials including
    discussion points, potential concerns, and communication strategies.

    Args:
        llm (Any): Language model instance.
        storage (JSONStorage): Storage instance.

    Returns:
        None

    Errors:
        ValueError: If inputs are invalid.
    """

    def __init__(self, llm: Any, storage: JSONStorage) -> None:
        """
        Initialize meeting preparation task.

        Args:
            llm (Any): Language model instance.
            storage (JSONStorage): Storage instance.

        Returns:
            None

        Errors:
            ValueError: If parameters are invalid.
        """
        self.llm = llm
        self.storage = storage
        logger.info("MeetingPrepTask initialized")

    def prepare_meeting(
        self,
        user_id: str,
        meeting_title: str,
        objective: str,
        audience: str,
        key_discussion_points: list[str],
        sensitivities: Optional[list[str]] = None,
        previous_context: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Generate comprehensive meeting preparation material.

        Args:
            user_id (str): User identifier.
            meeting_title (str): Title/name of the meeting.
            objective (str): Primary objective of the meeting.
            audience (str): Description of participants.
            key_discussion_points (list[str]): Key points to discuss.
            sensitivities (Optional[list[str]]): Sensitive topics or concerns.
            previous_context (Optional[str]): Previous meeting summary or context.

        Returns:
            dict[str, Any]: Comprehensive meeting preparation materials.

        Errors:
            ValueError: If inputs are invalid.
            Exception: If LLM API call fails.

        Example:
            Input:
                meeting_title="Q1 Performance Review",
                objective="Discuss performance and career growth",
                audience="Manager",
                key_discussion_points=["project completion", "team collaboration"],
                sensitivities=["salary discussion"]
            Output:
                {
                    "meeting_title": "...",
                    "opening_statement": "...",
                    "talking_points": [...],
                    "challenging_questions": [...],
                    "communication_tips": [...],
                    "checklist": [...]
                }
        """
        self._validate_inputs(meeting_title, objective, audience, key_discussion_points)

        try:
            # Generate talking points
            talking_points = self._generate_talking_points(objective, audience, key_discussion_points, previous_context)

            # Generate opening statement
            opening_statement = self._generate_opening(meeting_title, objective)

            # Identify potential challenging questions
            challenging_questions = self._identify_challenging_questions(
                objective, key_discussion_points, sensitivities
            )

            # Generate communication tips
            communication_tips = self._generate_communication_tips(audience, sensitivities)

            # Create preparation checklist
            checklist = self._create_checklist(key_discussion_points, sensitivities)

            result = {
                "meeting_id": f"{user_id}_{meeting_title}_{int(__import__('time').time())}",
                "meeting_title": meeting_title,
                "objective": objective,
                "audience": audience,
                "opening_statement": opening_statement,
                "talking_points": talking_points,
                "challenging_questions": challenging_questions,
                "communication_tips": communication_tips,
                "preparation_checklist": checklist,
                "key_discussion_points": key_discussion_points,
            }

            # Save preparation
            self.storage.save_meeting_prep(user_id, result)
            logger.info(f"Meeting preparation saved for user {user_id}")

            return result

        except Exception as e:
            logger.error(f"Failed to prepare meeting: {e}")
            raise

    def _validate_inputs(
        self, meeting_title: str, objective: str, audience: str, key_discussion_points: list[str]
    ) -> None:
        """
        Validate meeting preparation inputs.

        Args:
            meeting_title (str): Meeting title.
            objective (str): Meeting objective.
            audience (str): Audience description.
            key_discussion_points (list[str]): Discussion points.

        Returns:
            None

        Errors:
            ValueError: If validation fails.

        Example:
            Input: meeting_title="Review", objective="Discuss performance"
            Output: None (validation passed)
        """
        if not meeting_title or not meeting_title.strip():
            raise ValueError("Meeting title cannot be empty")

        if not objective or not objective.strip():
            raise ValueError("Meeting objective cannot be empty")

        if not audience or not audience.strip():
            raise ValueError("Audience description cannot be empty")

        if not key_discussion_points or len(key_discussion_points) == 0:
            raise ValueError("At least one discussion point is required")

    def _generate_talking_points(
        self,
        objective: str,
        audience: str,
        key_discussion_points: list[str],
        previous_context: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """
        Generate structured talking points for the meeting.

        Args:
            objective (str): Meeting objective.
            audience (str): Audience description.
            key_discussion_points (list[str]): Key points to discuss.
            previous_context (Optional[str]): Previous meeting context.

        Returns:
            list[dict[str, str]]: Structured talking points with explanations.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: objective="Performance review", key_discussion_points=["Q1 achievements"]
            Output: [{"point": "Q1 Achievements", "talking_points": [...], "supporting_evidence": "..."}]
        """
        context_text = f"Previous context: {previous_context}" if previous_context else ""

        prompt = f"""Generate structured talking points for this meeting:
        
        Objective: {objective}
        Audience: {audience}
        Discussion Points: {", ".join(key_discussion_points)}
        {context_text}
        
        For each discussion point, provide:
        1. Main point summary
        2. 2-3 supporting talking points
        3. Evidence or examples
        
        Format as JSON array:
        [{{
            "point": "discussion point",
            "summary": "brief summary",
            "talking_points": ["point 1", "point 2", "point 3"],
            "supporting_evidence": "example or data"
        }}]
        
        Return ONLY valid JSON array."""

        try:
            response = self.llm.invoke(prompt)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Failed to generate talking points: {e}")
            raise

    def _generate_opening(self, meeting_title: str, objective: str) -> str:
        """
        Generate an effective opening statement.

        Args:
            meeting_title (str): Meeting title.
            objective (str): Meeting objective.

        Returns:
            str: Professional opening statement.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: meeting_title="Project Update", objective="Update on deliverables"
            Output: "Thank you for taking the time to meet. Today, I'd like to update you on..."
        """
        prompt = f"""Generate a professional, confident opening statement for this meeting:
        
        Title: {meeting_title}
        Objective: {objective}
        
        The opening should:
        - Thank the attendee(s)
        - Briefly state the objective
        - Set a positive tone
        - Be 2-3 sentences maximum
        
        Return ONLY the opening statement, no other text."""

        try:
            return self.llm.invoke(prompt)
        except Exception as e:
            logger.error(f"Failed to generate opening statement: {e}")
            raise

    def _identify_challenging_questions(
        self, objective: str, key_discussion_points: list[str], sensitivities: Optional[list[str]] = None
    ) -> list[dict[str, str]]:
        """
        Identify potentially challenging questions and prepare responses.

        Args:
            objective (str): Meeting objective.
            key_discussion_points (list[str]): Discussion points.
            sensitivities (Optional[list[str]]): Sensitive topics.

        Returns:
            list[dict[str, str]]: Potential challenging questions with suggested responses.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: objective="Salary negotiation", sensitivities=["budget constraints"]
            Output: [{"question": "Why the increase?", "response": "Based on market research..."}]
        """
        sensitivities_text = f"Sensitive topics: {', '.join(sensitivities)}" if sensitivities else ""

        prompt = f"""Anticipate 3-5 potentially challenging or difficult questions for this meeting:
        
        Objective: {objective}
        Discussion Points: {", ".join(key_discussion_points)}
        {sensitivities_text}
        
        For each question, provide a professional, diplomatic response.
        
        Format as JSON array:
        [{{
            "question": "challenging question",
            "suggested_response": "professional response",
            "communication_tip": "how to deliver confidently"
        }}]
        
        Return ONLY valid JSON array."""

        try:
            response = self.llm.invoke(prompt)
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to identify challenging questions: {e}")
            return []

    def _generate_communication_tips(self, audience: str, sensitivities: Optional[list[str]] = None) -> list[str]:
        """
        Generate tailored communication tips for the audience.

        Args:
            audience (str): Audience description.
            sensitivities (Optional[list[str]]): Sensitive topics.

        Returns:
            list[str]: Communication tips and best practices.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: audience="Senior manager", sensitivities=["budget"]
            Output: ["Be concise and data-driven", "Focus on ROI", "Acknowledge constraints"]
        """
        sensitivities_text = f"Sensitive areas: {', '.join(sensitivities)}" if sensitivities else ""

        prompt = f"""Generate 4-6 specific communication tips for this audience:
        
        Audience: {audience}
        {sensitivities_text}
        
        Tips should cover tone, pacing, body language, and handling sensitivities.
        Return as JSON array of strings:
        ["tip 1", "tip 2", ...]
        
        Return ONLY the JSON array."""

        try:
            response = self.llm.invoke(prompt)
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to generate communication tips: {e}")
            return ["Speak clearly and confidently", "Listen actively", "Ask clarifying questions"]

    def _create_checklist(
        self, key_discussion_points: list[str], sensitivities: Optional[list[str]] = None
    ) -> list[dict[str, str]]:
        """
        Create a preparation checklist.

        Args:
            key_discussion_points (list[str]): Discussion points.
            sensitivities (Optional[list[str]]): Sensitive topics.

        Returns:
            list[dict[str, str]]: Checklist items.

        Errors:
            Exception: If LLM call fails.

        Example:
            Input: key_discussion_points=["Budget approval"]
            Output: [
                {"task": "Gather financial data", "category": "preparation"},
                {"task": "Practice opening statement", "category": "practice"}
            ]
        """
        sensitivities_text = f"Sensitive items: {', '.join(sensitivities)}" if sensitivities else ""

        prompt = f"""Create a preparation checklist for this meeting:
        
        Discussion Points: {", ".join(key_discussion_points)}
        {sensitivities_text}
        
        Include tasks for: research, practice, materials, mental preparation, etc.
        
        Format as JSON array:
        [{{
            "task": "what to do",
            "category": "preparation|practice|materials|other",
            "priority": "high|medium|low"
        }}]
        
        Return ONLY valid JSON array."""

        try:
            response = self.llm.invoke(prompt)
            return json.loads(response)
        except Exception as e:
            logger.warning(f"Failed to create checklist: {e}")
            return [
                {"task": "Review meeting objective and key points", "category": "preparation", "priority": "high"},
                {"task": "Prepare supporting documents", "category": "materials", "priority": "high"},
                {"task": "Practice opening statement", "category": "practice", "priority": "medium"},
            ]

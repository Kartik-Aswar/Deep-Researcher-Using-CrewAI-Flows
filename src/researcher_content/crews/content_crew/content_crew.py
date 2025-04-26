from crewai import Crew, Process
from src.researcher_content.crews.content_crew.config.agents import content_writer, content_reviewer
from src.researcher_content.crews.content_crew.config.tasks import write_section_task, review_section_task

class ContentCrew:
    """Content writing crew"""

    def __init__(self):
        # Use the pre-configured agents directly
        self.writer = content_writer
        self.reviewer = content_reviewer
        
        # Initialize tasks
        self.write_task = write_section_task
        self.review_task = review_section_task

    def crew(self) -> Crew:
        """Creates and returns the content writing crew"""
        # Assign agents to tasks
        self.write_task.agent = self.writer
        self.review_task.agent = self.reviewer
        self.review_task.context = [self.write_task]

        return Crew(
            agents=[self.writer, self.reviewer],
            tasks=[self.write_task, self.review_task],
            process=Process.sequential,
            verbose=True,
        )
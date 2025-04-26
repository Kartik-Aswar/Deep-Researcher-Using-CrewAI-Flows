from crewai import Task

from src.researcher_content.crews.content_crew.config.agents import content_reviewer,content_writer

write_section_task = Task(
  description='''Write a comprehensive section on the topic: {section_title} 
  Section description: {section_description}
  Target audience: {audience_level} level learners

  Your content should:
  1. Begin with a brief introduction to the section topic
  2. Research current trends, statistics, and developments using the search tool
  3. Explain all key concepts clearly with up-to-date examples
  4. Include practical applications or exercises where appropriate
  5. End with a summary of key points and future projections
  6. Be approximately 500-800 words in length

  Format your content in Markdown with appropriate headings, lists, and emphasis.

  Previously written sections:
  {previous_sections}

  Use the search tool to ensure information is current and relevant, especially for time-sensitive topics.
  Maintain consistency with previously written sections and build upon established concepts.''',
  expected_output="A well-structured, comprehensive section in Markdown format with current information from authoritative sources.",
  agent=content_writer
)

review_section_task = Task(
  description = '''
    Review and improve the following section on "{section_title}":

    {draft_content}

    Target audience: {audience_level} level learners

    Previously written sections:
    {previous_sections}

    Your review should:
    1. Fix any grammatical or spelling errors
    2. Improve clarity and readability
    3. Ensure content is comprehensive and accurate
    4. Verify consistency with previously written sections
    5. Enhance the structure and flow
    6. Add any missing key information

    Provide the improved version of the section in Markdown format.''',
  expected_output = " An improved, polished version of the section that maintains the original structure but enhances clarity, accuracy, and consistency.",
  agent = content_reviewer,
  context= [write_section_task] )


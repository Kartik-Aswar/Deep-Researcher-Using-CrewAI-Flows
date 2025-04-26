#!/usr/bin/env python
import json
from typing import List, Dict
from pydantic import BaseModel, Field
from crewai import LLM
from crewai.flow.flow import Flow, listen, start
from src.researcher_content.crews.content_crew.content_crew import ContentCrew

# Define our models for structured data
class Section(BaseModel):
    title: str = Field(description="Title of the section") # has to give input compulsory as no default value provide even though it (field) does not have ...
    description: str = Field(description="Brief description of what the section should cover")

class GuideOutline(BaseModel):
    title: str = Field(description="Title of the guide")
    introduction: str = Field(description="Introduction to the topic")
    target_audience: str = Field(description="Description of the target audience")
    sections: List[Section] = Field(description="List of sections in the guide")
    conclusion: str = Field(description="Conclusion or summary of the guide")

# Define our flow state
class GuideCreatorState(BaseModel):
    topic: str = ""
    audience_level: str = ""
    guide_outline: GuideOutline = None
    sections_content: Dict[str, str] = {}

class GuideCreatorFlow(Flow[GuideCreatorState]):
    """Flow for creating a comprehensive guide on any topic"""

    @start()
    def get_user_input(self):
        """Get input from the user about the guide topic and audience"""
        print("\n=== Create Your Comprehensive Guide ===\n")

        # Get user input
        self.state.topic = input("What topic would you like to create a guide for? ")

        # Get audience level with validation
        while True:
            audience = input("Who is your target audience? (beginner/intermediate/advanced) ").lower()
            if audience in ["beginner", "intermediate", "advanced"]:
                self.state.audience_level = audience
                break
            print("Please enter 'beginner', 'intermediate', or 'advanced'")

        print(f"\nCreating a guide on {self.state.topic} for {self.state.audience_level} audience...\n")
        return self.state

    @listen(get_user_input)
    def create_guide_outline(self, state):#here the state comes from the above function as @listen above function. here in create_guide_outline that state is just a varaible name and it can be anything but the value it will store will be the output of get_user_input function only.
        """Create a structured outline for the guide using a direct LLM call"""
        print("Creating guide outline...")

        # Initialize the LLM
        llm = LLM(model="gemini/gemini-2.0-flash",temperature=0.7, response_format=GuideOutline)

        # Create the messages for the outline
        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": f"""
            Create a detailed outline for a comprehensive guide on "{state.topic}" for {state.audience_level} level learners.

            The outline should include:
            1. A compelling title for the guide
            2. An introduction to the topic
            3. 4-6 main sections that cover the most important aspects of the topic
            4. A conclusion or summary

            For each section, provide a clear title and a brief description of what it should cover.
            """}
        ]

        # Make the LLM call with JSON response format
        response = llm.call(messages=messages) #It is in JSON format — meaning it’s a big string that looks like a dictionary but is actually a string.

        # Parse the JSON response
        outline_dict = json.loads(response) #json.loads(response) loads (parses) that JSON string and converts it into a Python dictionary (outline_dict).
        #Now, you take that Python dictionary (outline_dict) and convert it into a Pydantic model (GuideOutline).
        #GuideOutline(**outline_dict) means you are unpacking the dictionary keys and passing them as named parameters to create a typed, structured GuideOutline object
        self.state.guide_outline = GuideOutline(**outline_dict)

        # Save the outline to a file
        with open("output/guide_outline.json", "w") as f:
            json.dump(outline_dict, f, indent=2)

        print(f"Guide outline created with {len(self.state.guide_outline.sections)} sections")
        return self.state.guide_outline

    @listen(create_guide_outline)
    def write_and_compile_guide(self, outline):
        """Write all sections and compile the guide"""
        print("Writing guide sections and compiling...")
        completed_sections = [] #completed_sections is a list (holding titles only of sections you have already processed).

        # Process sections one by one to maintain context flow
        for section in outline.sections:
            print(f"Processing section: {section.title}")

            # Build context from previous sections
            previous_sections_text = "" #You create an empty string to collect all previously written sections' content
            if completed_sections:
                previous_sections_text = "# Previously Written Sections\n\n"    #If any sections are already completed you prepare a heading like written here and it is like (adding a big title in Markdown format.)
                for title in completed_sections: # as completed sections contains titles only 
                    previous_sections_text += f"## {title}\n\n" 
                    previous_sections_text += self.state.sections_content.get(title, "") + "\n\n" #self.state.sections_content.get("Title name of completed section", "") fetches the actual content of that section fot that title only and adds that content to previous written text.
            else:
                previous_sections_text = "No previous sections written yet."

            # Run the content crew for this section
            result = ContentCrew().crew().kickoff(inputs={
                "section_title": section.title,
                "section_description": section.description,
                "audience_level": self.state.audience_level,
                "previous_sections": previous_sections_text,
                "draft_content": ""
            })

            # Store the content
            self.state.sections_content[section.title] = result.raw #self.state.sections_content is a dictionary where we store: Key = the section title  result.raw means the final raw text (the actual written content) that was generated after the ContentCrew finished writing and reviewing and .raw as agents also creates additional meatadata like time, agent id etc so .raw gives useful text info only.
            completed_sections.append(section.title)
            print(f"Section completed: {section.title}")
        """the outline here is simply a parameter that automatically receives the result (the output) from the previous function create_guide_outline.

            And what does create_guide_outline return?
            👉 It returns self.state.guide_outline.

            And what is self.state.guide_outline?

            It is an object of type GuideOutline, which you defined earlier
        """
        # Compile the final guide
        guide_content = f"# {outline.title}\n\n"
        guide_content += f"## Introduction\n\n{outline.introduction}\n\n"

        # Add each section in order
        for section in outline.sections:
            section_content = self.state.sections_content.get(section.title, "")
            guide_content += f"\n\n{section_content}\n\n"

        # Add conclusion
        guide_content += f"## Conclusion\n\n{outline.conclusion}\n\n"

        # Save the guide
        with open("output/complete_guide.md", "w") as f:
            f.write(guide_content)

        print("\nComplete guide compiled and saved to output/complete_guide.md")
        return "Guide creation completed successfully"

def kickoff():
    """Run the guide creator flow"""
    GuideCreatorFlow().kickoff()
    print("\n=== Flow Complete ===")
    print("Your comprehensive guide is ready in the output directory.")
    print("Open output/complete_guide.md to view it.")

def plot():
    """Generate a visualization of the flow"""
    flow = GuideCreatorFlow()
    flow.plot("guide_creator_flow")
    print("Flow visualization saved to guide_creator_flow.html")

if __name__ == "__main__":
    kickoff()
    plot()
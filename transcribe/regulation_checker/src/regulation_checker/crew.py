from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
import mlflow
import os
from dotenv import load_dotenv
load_dotenv()
mlflow.crewai.autolog()

# Optional: Set a tracking URI and an experiment name if you have a tracking server
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("CrewAI")


from crewai_tools import JSONSearchTool

json_tool = JSONSearchTool(
    json_path='\\data.json',  # Optional: specify your JSON file
    config={
        "llm": {
            "provider": "google",  # Use Google as provider
            "config": {
                "model": "gemini-pro",  # or gemini-1.5-pro, etc.
                # Optional configurations:
                # "temperature": 0.5,
                # "top_p": 1,
            },
        },
        "embedding_model": {
            "provider": "google",  # Google embeddings
            "config": {
                "model": "models/embedding-001",  # Google's embedding model
                "task_type": "retrieval_document",
            },
        },
    }
)

@CrewBase
class RegulationChecker():
    """RegulationChecker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @agent
    def compliance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_analyst'], # type: ignore[index]
            verbose=True,
            planning=True,
            tools=[json_tool]
        )
    
    @agent
    def compliance_reporter(self) -> Agent:
        return Agent(
            config=self.agents_config['compliance_reporter'], # type: ignore[index]
            verbose=True,
            allow_delegation=True,
            planning=True,
            tools=[json_tool]  # Reporter also has access to verify findings if needed
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def compliance_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['compliance_analysis_task'], # type: ignore[index]
            agent=self.compliance_analyst()
        )
    
    @task
    def compliance_reporting_task(self) -> Task:
        return Task(
            config=self.tasks_config['compliance_reporting_task'], # type: ignore[index]
            agent=self.compliance_reporter(),
            context=[self.compliance_analysis_task()]  # Receives output from analysis task
        )

    @crew
    def crew(self) -> Crew:
        """Creates the RegulationChecker crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

# Example usage - you can modify the transcript_segment as needed
if __name__ == "__main__":
    result = RegulationChecker().crew().kickoff(inputs={"transcript_segment": "انا عرضت data العملاء علي اخويا وهو قالي كدا"})
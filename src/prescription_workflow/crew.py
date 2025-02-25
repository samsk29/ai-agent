from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from src.prescription_workflow.tools.email_tool import EmailTools

llm = LLM(model="ollama/llama3.2", base_url="http://localhost:11434")

@CrewBase
class PrescriptionWorkflow:
    """PrescriptionWorkflow crew that parses email content, validates required fields,
       and sends follow-up emails if fields are missing.
    """

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def email_reader(self) -> Agent:
        """
        Parses the email content.
        """
        return Agent(
            config=self.agents_config['email_reader'],
            llm=llm,
            allow_delegation=False,
            verbose=True
        )

    @agent
    def intake(self) -> Agent:
        """
        Validates required prescription fields from the parsed email content.
        If all required fields are present, saves the validated data to a JSON file.
        If not, it flags the missing fields to be handled by the response agent.
        """
        return Agent(
            config=self.agents_config['intake'],
            tools=[EmailTools.extract_prescription_fields_from_emails],
            llm=llm,
            verbose=True
        )

    @agent
    def response(self) -> Agent:
        """
        Handles missing prescription fields.
        Sends an email to the patient requesting the missing information.
        """
        return Agent(
            config=self.agents_config['response'],
            tools=[EmailTools.send_email, EmailTools.handle_missing_fields],
            llm=llm,
            verbose=True
        )

    @task
    def parse_and_triage_task(self) -> Task:
        """
        Task for parsing the input email content.
        This task uses the email_reader agent to fetch unread emails and extract:
          - Message ID
          - Subject
          - Sender
          - Full email body
        """
        return Task(
            config=self.tasks_config['parse_and_triage_task']
        )

    @task
    def intake_validation_task(self) -> Task:
        """
        Task for validating the parsed email content.
        The intake agent checks the email data for all necessary prescription fields.
        If all required fields are present, the data is saved to a JSON file.
        If any fields are missing, these are passed to the response agent.
        """
        return Task(
            config=self.tasks_config['intake_validation_task']
        )

    @task
    def response_handling_task(self) -> Task:
        """
        Task for handling missing prescription fields.
        The response agent sends an email to the patient requesting the missing information.
        """
        return Task(
            config=self.tasks_config['response_handling_task']
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the Prescription Workflow crew."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

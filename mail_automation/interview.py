import streamlit as st
import pandas as pd
import smtplib
from email.message import EmailMessage
import requests
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import Field
from dotenv import load_dotenv


# Streamlit UI
st.title("Email Automation for Job Candidates")
st.write("This app automates the process of sending emails to job candidates based on their application status.")

calendly_link = st.text_input("Calendly Link")
hr_name = st.text_input("HR Name")
job_title = st.text_input("Job Title")
sender_email = st.text_input("Your Email")
sender_password = st.text_input("Your Email Password", type="password")
csv_file = st.file_uploader("Upload CSV with columns 'name', 'email', 'status'", type=["csv"])
send_emails = st.checkbox("Send Emails Automatically")

# Context Tool for shared info
class ContextTool(BaseTool):
    name: str = "context_tool"
    description: str = "Provides shared context like HR name and Calendly link."

    calendly_link: str = Field(default="")
    hr_name: str = Field(default="")
    job_title: str = Field(default="")

    def _run(self, *args, **kwargs):
        return f"Calendly: {self.calendly_link}, HR: {self.hr_name}, Job: {self.job_title}"

    async def _arun(self, *args, **kwargs):
        return self._run()


context_tool = ContextTool(
    calendly_link=calendly_link,
    hr_name=hr_name,
    job_title=job_title
)

# Define Agents
csv_extractor = Agent(
    name="CSV Data Extractor",
    role="Data extraction specialist who reads and processes CSV files",
    goal="Extract candidate information from CSV files accurately",
    backstory="A data processing expert who specializes in extracting and organizing information from CSV files",
    llm=llm,
    tools=[],
    verbose=False
)

email_creator = Agent(
    name="Email Template Generator",
    role="Email content creator",
    goal="Create a standard template email for job candidates",
    backstory="An experienced professional who creates standardized emails for job candidates",
    llm=llm,
    tools=[context_tool],
    verbose=False
)

output_formatter = Agent(
    name="Email Output Formatter",
    role="Formats and prepares emails for sending",
    goal="Format emails consistently with proper structure",
    backstory="A formatting specialist who ensures emails are properly structured and ready for sending",
    llm=llm,
    tools=[context_tool],
    verbose=False
)

# Email sending function
def send_email(to, subject, body, sender, password):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender, password)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return str(e)

# Main email generation logic
if csv_file and st.button("Generate Emails"):
    df = pd.read_csv(csv_file)

    for _, row in df.iterrows():
        name = row["name"]
        email = row["email"]
        status = row.get("status", "interview_invite").strip().lower()

        # Step 1: Extract candidate info (simulate)
        task_extract = Task(
            description=f"Extract the following candidate info: name={name}, email={email}, status={status}",
            expected_output="Candidate info extracted and confirmed",
            agent=csv_extractor
        )

        # Step 2: Create email template based on status
        if status == "interview_invite":
            email_prompt = (
                f"Write a professional interview invitation email for {name} "
                f"for the position of {job_title}. Include the Calendly link: {calendly_link}. "
                f"Sign the email with {hr_name}."
            )
            subject = f"Interview Invitation for {job_title}"
        elif status == "rejection":
            email_prompt = (
                f"Write a polite rejection email for {name} regarding the {job_title} position. "
                f"Thank them for their interest and encourage them to apply again in the future."
            )
            subject = f"Application Update for {job_title}"
        elif status == "follow_up":
            email_prompt = (
                f"Write a follow-up email to {name} reminding them about the interview invitation "
                f"for {job_title} and include the Calendly link: {calendly_link}."
            )
            subject = f"Follow-up on your {job_title} Application"
        elif status == "reschedule":
            email_prompt = (
                f"Write an email to {name} to reschedule their interview for the {job_title} position. "
                f"Include the Calendly link: {calendly_link} and apologize for the inconvenience."
            )
            subject = f"Interview Rescheduling for {job_title}"
        else:
            st.warning(f"Unknown status '{status}' for {name}, skipping.")
            continue

        task_create = Task(
            description=email_prompt,
            expected_output="Draft email content",
            agent=email_creator
        )

        # Step 3: Format final output email
        task_format = Task(
            description=(
                f"Format the following email professionally. Add greeting to {name} and closing with {hr_name}: {email_prompt}"
            ),
            expected_output="Final formatted email",
            agent=output_formatter
        )

        crew = Crew(
            agents=[csv_extractor, email_creator, output_formatter],
            tasks=[task_extract, task_create, task_format],
            verbose=False
        )

        email_body = crew.kickoff()

        st.subheader(f"Email for {name} ({status})")
        st.text_area("Generated Email", email_body, height=220)

        if send_emails and sender_email and sender_password:
            send_status = send_email(
                to=email,
                subject=subject,
                body=email_body,
                sender=sender_email,
                password=sender_password
            )
            if send_status is True:
                st.success(f"Email sent successfully to {email}")
            else:
                st.error(f"Failed to send email to {email}: {send_status}")


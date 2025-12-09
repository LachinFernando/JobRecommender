import os
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import  Annotated, List
import operator
from openai import OpenAI
import base64
from typing import TypedDict, Annotated, List, Dict
import streamlit as st

from prompts import CAREER_RECOMMENDATION_PROMPT, SKILLS_PROMPT


os.environ["LANGCHAIN_TRACING_V2"] = st.secrets["llm"]["LANGCHAIN_TRACING_V2"]
os.environ["LANGCHAIN_API_KEY"] = st.secrets["llm"]["LANGCHAIN_API_KEY"]
os.environ["LANGCHAIN_ENDPOINT"] = st.secrets["llm"]["LANGCHAIN_ENDPOINT"]
os.environ["LANGCHAIN_PROJECT"] = st.secrets["llm"]["LANGCHAIN_PROJECT"]
os.environ["OPENAI_API_KEY"] = st.secrets["llm"]["OPENAI_API_KEY"]

# use gpt 5
MODEL = "gpt-5-mini"

# set the openai model
llm = ChatOpenAI(model=MODEL, temperature=0)

class JobDescription(BaseModel):
    title: str = Field(description="Title of the job")
    description: str = Field(description="Description of the job")
    skills: str = Field(description="Set of skills required for the job separated by commas")
    daily_duties: str = Field(description="Set of daily duties for the job separated by commas")
    

class CareerRecommendation(BaseModel):
    careers: List[JobDescription] = Field(description="List of career recommendations")

class SkillDescription(BaseModel):
    skill: str = Field(description="Title of the skill")
    description: str = Field(description="Description of the skill")
    skills: str = Field(description="Set of skills required for the skill separated by commas")
    daily_duties: str = Field(description="Set of daily duties for the skill separated by commas")

class SkillPipeline(BaseModel):
    skills: List[SkillDescription] = Field(description="List of skills required for the job separated by commas")


def career_recommendation(education_level: str, field_of_study: str, career_goals: str, interests: str, skills: str) -> CareerRecommendation:
    # create the system message
    system_message = SystemMessage(content=CAREER_RECOMMENDATION_PROMPT.format(education_level=education_level, field_of_study=field_of_study, career_goals=career_goals, interests=interests, skills=skills))
    # create structured output
    structured_llm = llm.with_structured_output(CareerRecommendation)
    # invoke the llm
    response = structured_llm.invoke([system_message])
    
    return response


def skill_pipeline(job_title: str) -> SkillPipeline:
    # create the system message
    system_message = SystemMessage(content=SKILLS_PROMPT.format(job_title=job_title))
    # create structured output
    structured_llm = llm.with_structured_output(SkillPipeline)
    # invoke the llm
    response = structured_llm.invoke([system_message])
    
    return response
    
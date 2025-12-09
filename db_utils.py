import boto3
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Union, Any
from boto3.dynamodb.conditions import Key
import streamlit as st

# Load environment variables from secrets
os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY"]
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_KEY"]
os.environ["AWS_REGION"] = st.secrets["aws"]["REGION_NAME"]


# add user info to dynamodb
def add_user_info(
    table_name: str,
    user_id: str,
    first_name: str,
    last_name: str,
    email: str,
    education_level: str,
    field_of_study: str,
    interests: List[str],
    skills: List[str],
    career_goals: str,
    creation_date: Optional[str] = None,
    additional_attributes: Optional[Dict] = None
) -> Dict:
    """
    Add a new record to the specified DynamoDB table.
    
    Args:
        table_name (str): Name of the DynamoDB table
        user_id (str): User ID associated with the record
        first_name (str): First name of the user
        last_name (str): Last name of the user
        email (str): Email of the user
        education_level (str): Education level of the user
        field_of_study (str): Field of study of the user
        interests (List[str]): Interests of the user
        skills (List[str]): Skills of the user
        career_goals (str): Career goals of the user
        creation_date (str, optional): ISO format datetime string. Defaults to current datetime.
        additional_attributes (Dict, optional): Additional attributes to store. Defaults to None.
        
    Returns:
        Dict: The response from DynamoDB with success/error information
    """
    # Initialize AWS session and DynamoDB resource
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Prepare the item
    item = {
        'user_id': user_id,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'education_level': education_level,
        'field_of_study': field_of_study,
        'interests': interests,
        'skills': skills,
        'career_goals': career_goals,
        'creation_date': creation_date or datetime.utcnow().isoformat(),
    }
    
    # Add any additional attributes if provided
    if additional_attributes:
        item.update(additional_attributes)
    
    try:
        # Put the item in the table
        response = table.put_item(Item=item)
        return {
            'success': True,
        }
    except Exception as e:
        return {
            'success': False,
        }


@st.cache_data
def get_record(
    table_name: str,
    user_id: str
) -> Optional[Dict[str, Any]]:
    """
    Retrieve a record from the specified DynamoDB table by user_id.
    
    Args:
        table_name (str): Name of the DynamoDB table
        user_id (str): The ID of the user to retrieve
        
    Returns:
        Optional[Dict]: The record if found, None otherwise. The response includes
        the item attributes if found, or None if not found.
    """
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    try:
        response = table.get_item(
            Key={
                'user_id': user_id
            }
        )
        
        # The item will be in the 'Item' key if found
        return response.get('Item')
        
    except Exception as e:
        print(f"Error getting record: {str(e)}")
        return None
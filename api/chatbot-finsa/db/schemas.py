from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class UserInput(BaseModel):
    question: str
    attempts: int

class AgentState(BaseModel):
    question: str
    sql_query: Optional[str] = None
    query_result: Optional[Any] = None
    query_rows: Optional[List[Dict[str, Any]]] = None
    relevance: Optional[str] = None
    sql_error: Optional[bool] = False
    attempts: int = 0

class CheckRelevance(BaseModel):
    relevance: str = Field(
        description="Indicates whether the question is related to the database schema. 'relevant' or 'not_relevant'."
    )

class ConvertToSQL(BaseModel):
    sql_query: str = Field(
        description="The SQL query corresponding to the user's natural language question."
    )

class RewrittenQuestion(BaseModel):
    question: str = Field(description="The rewritten question.")

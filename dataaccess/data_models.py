from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AgentQueryLog(Base):
    __tablename__ = "agent_query_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    tool_used = Column(String)        # which tool(s) the agent picked
    answer = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

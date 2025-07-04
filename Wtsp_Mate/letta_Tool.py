from agno.tools import BaseTool
from letta_client import Letta, MessageCreate

class LettaTool(BaseTool):
    def __init__(self, token: str, project: str, agent_id: str):
        super().__init__(name="letta_tool")
        self.letta_client = Letta(token=token, project=project)
        self.agent_id = agent_id

    def execute(self, message: str) -> str:
        """Send a message to Letta and return the response."""
        try:
            letta_msg = MessageCreate(role="user", content=message)
            letta_response = self.letta_client.agents.messages.create(
                agent_id=self.agent_id,
                messages=[letta_msg],
            )
            # Extract the response content
            for msg in letta_response.messages:
                if hasattr(msg, "content") and msg.content:
                    return msg.content
            return "Sorry, no response received from Letta."
        except Exception as e:
            return f"Error communicating with Letta: {str(e)}"
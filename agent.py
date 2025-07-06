

# Import required modules
from datetime import datetime
from uuid import uuid4
from uagents import Agent, Protocol, Context
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)
# Import get_token_balances from token_balance_checker
from balance_checker import get_token_balances
# Initialise agent
agent = Agent(
    name="AnInch",
    seed="secret_seed_phrase123123",
    publish_agent_details=True,
    mailbox=True,
)

# Initialize the chat protocol
chat_proto = Protocol(spec=chat_protocol_spec)


# Startup Handler - Print agent details
@agent.on_event("startup")
async def startup_handler(ctx: Context):
    # Print agent details
    ctx.logger.info(f"My name is {ctx.agent.name} and my address is {ctx.agent.address}")

# Message Handler - Process received messages and send acknowledgements
@chat_proto.on_message(ChatMessage)
async def handle_message(ctx: Context, sender: str, msg: ChatMessage):
    for item in msg.content:
        if isinstance(item, TextContent):
            ctx.logger.info(f"Received message from {sender}: {item.text}")
            # Try to extract an Ethereum address from the message text
            address = item.text.strip()
            # Optionally, add validation for Ethereum address format
            try:
                balances = get_token_balances(address)
                if balances:
                    # Show only non-zero balances
                    nonzero = {k: v for k, v in balances.items() if str(v) != '0'}
                    if nonzero:
                        balance_str = '\n'.join([f"{token}: {balance}" for token, balance in nonzero.items()])
                    else:
                        balance_str = "No non-zero token balances found."
                else:
                    balance_str = "Could not fetch balances."
            except Exception as e:
                balance_str = f"Error fetching balance: {e}"

            # Send acknowledgment
            ack = ChatAcknowledgement(
                timestamp=datetime.utcnow(),
                acknowledged_msg_id=msg.msg_id
            )
            await ctx.send(sender, ack)

            # Send response message with balance info
            response = ChatMessage(
                timestamp=datetime.utcnow(),
                msg_id=uuid4(),
                content=[TextContent(type="text", text=f"Your balances: \n{balance_str}")]
            )
            await ctx.send(sender, response)

# Acknowledgement Handler - Process received acknowledgements
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

# Include the protocol in the agent to enable the chat functionality
# This allows the agent to send/receive messages and handle acknowledgements using the chat protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == '__main__':
    agent.run()
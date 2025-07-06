

# Import required modules
from datetime import datetime
from uuid import uuid4
from llm import get_completion
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
                        # Hardcoded mapping for known tokens
                        token_name_map = {
                            '0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48': 'USDC',
                            '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee': 'ETH',
                            'eth': 'ETH',
                            # Add more mappings here as needed
                        }
                        # Prepare original output, replacing mapped tokens
                        # Format balances with commas and up to 6 decimals for tokens
                        def format_balance(val):
                            try:
                                val_f = float(val)
                                if val_f == int(val_f):
                                    return f"{int(val_f):,}"
                                return f"{val_f:,.6f}".rstrip('0').rstrip('.')
                            except Exception:
                                return str(val)

                        original_lines = [
                            f"{token_name_map.get(token.lower(), token)}: {format_balance(balance)}"
                            for token, balance in nonzero.items()
                        ]
                        # Fetch USD prices
                        import requests
                        token_addresses = list(nonzero.keys())
                        # Treat both 'ETH' and '0xeeee...eeee' as ETH for price lookup
                        contract_addresses = ','.join([
                            addr.lower() for addr in token_addresses if addr.lower() not in ['eth', '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee']
                        ])
                        price_map = {}
                        if contract_addresses:
                            price_url = f'https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={contract_addresses}&vs_currencies=usd'
                            price_resp = requests.get(price_url)
                            if price_resp.status_code == 200:
                                price_map = price_resp.json()
                        eth_price = None
                        eth_resp = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd')
                        if eth_resp.status_code == 200:
                            eth_price = eth_resp.json().get('ethereum', {}).get('usd')
                        usd_lines = []
                        for token, balance in nonzero.items():
                            usd_value = None
                            token_lc = token.lower()
                            token_label = token_name_map.get(token_lc, token)
                            # ETH handling: both 'ETH' and '0xeeee...eeee'
                            if token_lc in ['eth', '0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'] and eth_price:
                                try:
                                    usd_value = float(balance) * float(eth_price)
                                except Exception:
                                    usd_value = None
                            elif token_lc in price_map:
                                try:
                                    usd_value = float(balance) * float(price_map[token_lc]['usd'])
                                except Exception:
                                    usd_value = None
                            if usd_value is not None:
                                usd_lines.append(f"{token_label} (USD): ${usd_value:,.2f}")
                            else:
                                usd_lines.append(f"{token_label} (USD): N/A")
                        balance_str = '\n'.join(original_lines) + '\n' + '\n'.join(usd_lines)
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
                content=[TextContent(type="text", text=f"Your Token balances: \n{balance_str}")]
            )
            await ctx.send(sender, response)

async def send_message(ctx: Context, sender, msg: ChatMessage):
    completion = await get_completion(context="", prompt=msg.content[0].text)
 
    await ctx.send(sender, ChatMessage(
        timestamp=datetime.now(),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=completion["choices"][0]["message"]["content"])],
    ))

# Acknowledgement Handler - Process received acknowledgements
@chat_proto.on_message(ChatAcknowledgement)
async def handle_acknowledgement(ctx: Context, sender: str, msg: ChatAcknowledgement):
    ctx.logger.info(f"Received acknowledgement from {sender} for message: {msg.acknowledged_msg_id}")

# Include the protocol in the agent to enable the chat functionality
# This allows the agent to send/receive messages and handle acknowledgements using the chat protocol
agent.include(chat_proto, publish_manifest=True)

if __name__ == '__main__':
    agent.run()
import os
import requests

def get_token_balances(wallet_address):
    endpoint = f'https://api.1inch.dev/balance/v1.2/1/balances/{wallet_address}'
    api_key = os.getenv('INCH_API_KEY')
    if not api_key:
        raise ValueError("INCH_API_KEY environment variable not set.")
    response = requests.get(endpoint, headers={'Authorization': f'Bearer {api_key}'})

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch token balances. Error code: {response.status_code}")
        return None

def main():
    # Replace '0xYourWalletAddress' with the Ethereum wallet address you want to check
    wallet_address = '0xBa978839eDBcECE04DD547C15509b6DdD8Ae0c0c'
    token_balances = get_token_balances(wallet_address)

    if token_balances:
        print(f"Token balances for wallet address {wallet_address}:")
        # Fetch token metadata from 1inch token list
        token_list_endpoint = 'https://api.1inch.dev/token/v1.2/1'
        api_key = os.getenv('INCH_API_KEY')
        token_list_resp = requests.get(token_list_endpoint, headers={'Authorization': f'Bearer {api_key}'})
        token_metadata = {}
        if token_list_resp.status_code == 200:
            token_metadata = token_list_resp.json().get('tokens', {})
        else:
            print("Warning: Could not fetch token metadata. Showing addresses only.")

        for token, balance in token_balances.items():
            if str(balance) != '0':
                name = token_metadata.get(token, {}).get('name', token)
                symbol = token_metadata.get(token, {}).get('symbol', '')
                if symbol:
                    print(f"{name} ({symbol}): {balance}")
                else:
                    print(f"{name}: {balance}")
    else:
        print("Token balance fetch failed. Please check your wallet address.")

if __name__ == '__main__':
    main()
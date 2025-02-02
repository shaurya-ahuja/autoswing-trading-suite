import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/swinggrid")

from binance_client import BinanceClientWrapper
import config

print("--- Testing Connection Logic ---")

# Test 1: Testnet (Default)
print("\n1. Testing Testnet (No Keys)...")
client = BinanceClientWrapper(use_mainnet=False)
print(f"Status: {client.connection_status}")
print(f"Base URL: {client.base_url}")
price = client.get_current_price()
print(f"Price: {price}")

# Test 2: Mainnet with Dummy Keys (Should Fail or Error)
print("\n2. Testing Mainnet (Dummy Keys)...")
client_main = BinanceClientWrapper(
    api_key="dummy_key", 
    api_secret="dummy_secret", 
    use_mainnet=True
)
print(f"Status: {client_main.connection_status}")
print(f"Base URL: {client_main.base_url}")
print(f"Last Error: {client_main.last_error}")

# Try fetching price (Should likely fail auth or fall back to REST)
# API key is invalid so REST will fail with 401 Unauthorized or similar
print("Attempting to fetch price...")
price_main = client_main.get_current_price()
print(f"Price (Simulated Fallback?): {price_main}")
print(f"Final Status: {client_main.connection_status}")
print(f"Final Error: {client_main.last_error}")

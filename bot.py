from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from eth_account.messages import encode_defunct
from eth_utils import to_hex
from eth_account import Account
from web3 import Web3
from colorama import *
from datetime import datetime
import asyncio, time, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Sowing:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Connection": "keep-alive",
            "Host": "sowing-api.taker.xyz",
            "Origin": "https://sowing.taker.xyz",
            "Referer": "https://sowing.taker.xyz/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": FakeUserAgent().random
        }
        self.BASE_API = "https://sowing-api.taker.xyz"
        self.PAGE_URL = "https://sowing.taker.xyz"
        self.SITE_KEY = "0x4AAAAAABNqF8H4KF9TDs2O"
        self.RPC_URL = "https://rpc-mainnet.taker.xyz/"
        self.ACTIVATE_ROUTER_ADDRESS = "0xF929AB815E8BfB84Cdab8d1bb53F22eB1e455378"
        self.ACTIVATE_CONTRACT_ABI = [
            {
                "constant": False,
                "inputs": [],
                "name": "active",
                "outputs": [],
                "payable": False,
                "stateMutability": "nonpayable",
                "type": "function"
            }
        ]
        self.REF_CODE = "ZRCD77BC" # U can change it with yours.
        self.CAPTCHA_KEY = None
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.access_tokens = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

      def welcome(self):
     print(
         f"""
    █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
   ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
   ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
   ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
   ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
   ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝  
     By : ADB NODE
     {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}SowingTaker - BOT
         """
         f"""
     {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<https://t.me/airdropbombnode>
         """
     )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_2captcha_key(self):
        try:
            with open("2captcha_key.txt", 'r') as file:
                captcha_key = file.read().strip()

            return captcha_key
        except Exception as e:
            return None
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, token):
        if token not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[token] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[token]

    def rotate_proxy_for_account(self, token):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[token] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def generate_address(self, account: str):
        try:
            account = Account.from_key(account)
            address = account.address
            
            return address
        except Exception as e:
            return None
        
    def mask_account(self, account):
        try:
            mask_account = account[:6] + '*' * 6 + account[-6:]
            return mask_account 
        except Exception as e:
            return None
    
    def generate_payload(self, account: str, address: str, nonce: str):
        try:
            encoded_message = encode_defunct(text=nonce)
            signed_message = Account.sign_message(encoded_message, private_key=account)
            signature = to_hex(signed_message.signature)

            payload = {
                "address":address, 
                "invitationCode":self.REF_CODE, 
                "message":nonce, 
                "signature":signature
            }
            
            return payload
        except Exception as e:
            raise Exception(f"Generate Req Payload Failed: {str(e)}")
        
    async def get_web3_with_check(self, address: str, use_proxy: bool, retries=3, timeout=60):
        request_kwargs = {"timeout": timeout}

        proxy = self.get_next_proxy_for_account(address) if use_proxy else None

        if use_proxy and proxy:
            request_kwargs["proxies"] = {"http": proxy, "https": proxy}

        for attempt in range(retries):
            try:
                web3 = Web3(Web3.HTTPProvider(self.RPC_URL, request_kwargs=request_kwargs))
                web3.eth.get_block_number()
                return web3
            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(3)
                    continue
                raise Exception(f"Failed to Connect to RPC: {str(e)}")
        
    async def get_token_balance(self, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            balance = web3.eth.get_balance(address)
            token_balance = balance / (10 ** 18)

            return token_balance
        except Exception as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}     Message :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None
        
    async def perform_onchain(self, account: str, address: str, use_proxy: bool):
        try:
            web3 = await self.get_web3_with_check(address, use_proxy)

            contract_address = web3.to_checksum_address(self.ACTIVATE_ROUTER_ADDRESS)
            token_contract = web3.eth.contract(address=contract_address, abi=self.ACTIVATE_CONTRACT_ABI)

            active_data = token_contract.functions.active()
            estimated_gas = active_data.estimate_gas({"from": address})

            max_priority_fee = web3.to_wei(0.001, "gwei")
            max_fee = max_priority_fee

            active_tx = active_data.build_transaction({
                "from": address,
                "gas": int(estimated_gas),
                "maxFeePerGas": int(max_fee),
                "maxPriorityFeePerGas": int(max_priority_fee),
                "nonce": web3.eth.get_transaction_count(address, "pending"),
                "chainId": web3.eth.chain_id,
            })

            signed_tx = web3.eth.account.sign_transaction(active_tx, account)
            raw_tx = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash = web3.to_hex(raw_tx)
            receipt = await asyncio.to_thread(web3.eth.wait_for_transaction_receipt, tx_hash, timeout=300)
            block_number = receipt.blockNumber

            return tx_hash, block_number
        except Exception as e:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT}   ● {Style.RESET_ALL}"
                f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} Perform On-Chain Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )
            return None, None
    
    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Run With Free Proxyscrape Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Run With Private Proxy{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Run Without Proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "With Free Proxyscrape" if choose == 1 else 
                        "With Private" if choose == 2 else 
                        "Without"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Run {proxy_type} Proxy Selected.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Rotate Invalid Proxy? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter 'y' or 'n'.{Style.RESET_ALL}")

        return choose, rotate
    
    async def solve_cf_turnstile(self, proxy=None, retries=5):
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:

                    if self.CAPTCHA_KEY is None:
                        return None
                    
                    url = f"http://2captcha.com/in.php?key={self.CAPTCHA_KEY}&method=turnstile&sitekey={self.SITE_KEY}&pageurl={self.PAGE_URL}"
                    async with session.get(url=url) as response:
                        response.raise_for_status()
                        result = await response.text()

                        if 'OK|' not in result:
                            await asyncio.sleep(5)
                            continue

                        request_id = result.split('|')[1]

                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Req Id  :{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {request_id} {Style.RESET_ALL}"
                        )

                        for _ in range(30):
                            res_url = f"http://2captcha.com/res.php?key={self.CAPTCHA_KEY}&action=get&id={request_id}"
                            async with session.get(url=res_url) as res_response:
                                res_response.raise_for_status()
                                res_result = await res_response.text()

                                if 'OK|' in res_result:
                                    turnstile_token = res_result.split('|')[1]
                                    return turnstile_token
                                elif res_result == "CAPCHA_NOT_READY":
                                    self.log(
                                        f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                        f"{Fore.BLUE+Style.BRIGHT}Message :{Style.RESET_ALL}"
                                        f"{Fore.YELLOW + Style.BRIGHT} Captcha Not Ready {Style.RESET_ALL}"
                                    )
                                    await asyncio.sleep(5)
                                    continue
                                else:
                                    break

            except Exception as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return None
    
    async def generate_nonce(self, address: str, proxy=None):
        url = f"{self.BASE_API}/wallet/generateNonce"
        data = json.dumps({"walletAddress":address})
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                f"{Fore.RED+Style.BRIGHT} GET Nonce Failed {Style.RESET_ALL}"
                f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
            )

        return None
    
    async def user_login(self, account: str, address: str, nonce: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/wallet/login"
        data = json.dumps(self.generate_payload(account, address, nonce))
        headers = {
            **self.headers,
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Login Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None
    
    async def user_info(self, address: str, proxy=None, retries=5):
        url = f"{self.BASE_API}/user/info"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}"
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Error  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} GET User Data Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )
            
        return None
    
    async def start_mining(self, address: str, turnstile_token: str, status: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/task/signIn?status={status}"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {self.access_tokens[address]}",
            "Cf-Turnstile-Token": turnstile_token,
        }
        await asyncio.sleep(3)
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.get(url=url, headers=headers) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.log(
                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                    f"{Fore.CYAN+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                    f"{Fore.RED+Style.BRIGHT} Activation Failed {Style.RESET_ALL}"
                    f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.YELLOW+Style.BRIGHT} {str(e)} {Style.RESET_ALL}"
                )

        return None
            
    async def process_generate_nonce(self, address: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            self.log(
                f"{Fore.CYAN+Style.BRIGHT}Proxy  :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {proxy} {Style.RESET_ALL}"
            )

            get_nonce = await self.generate_nonce(address, proxy)
            if get_nonce and get_nonce.get("message") == "SUCCESS":
                nonce = get_nonce["result"]["nonce"]
                    
                return nonce
            
            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(address)
                await asyncio.sleep(5)
                continue

            return False
            
    async def process_user_login(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        nonce = await self.process_generate_nonce(address, use_proxy, rotate_proxy)
        if nonce:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None

            login = await self.user_login(account, address, nonce, proxy)
            if login and login.get("message") == "SUCCESS":
                self.access_tokens[address] = login["result"]["token"]

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Status :{Style.RESET_ALL}"
                    f"{Fore.GREEN+Style.BRIGHT} Login Success {Style.RESET_ALL}"
                )
                return True
            
            return False
        
    async def process_activate_mining(self, account: str, address: str, use_proxy: bool):
        balance = await self.get_token_balance(address, use_proxy)
        tx_fees = 0.000000060305
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}Balance :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {balance} TAKER {Style.RESET_ALL}"
        )
        self.log(
            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
            f"{Fore.BLUE+Style.BRIGHT}Tx Fees :{Style.RESET_ALL}"
            f"{Fore.WHITE+Style.BRIGHT} {tx_fees} TAKER {Style.RESET_ALL}"
        )

        if not balance or balance < tx_fees:
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                f"{Fore.YELLOW+Style.BRIGHT} Insufficient TAKER Balance {Style.RESET_ALL}"
            )
            return False

        tx_hash, block_number = await self.perform_onchain(account, address, use_proxy)
        if tx_hash and block_number:
            explorer = f"https://explorer.taker.xyz/tx/{tx_hash}"

            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Block   :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {block_number} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Tx Hash :{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {tx_hash} {Style.RESET_ALL}"
            )
            self.log(
                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                f"{Fore.BLUE+Style.BRIGHT}Explorer:{Style.RESET_ALL}"
                f"{Fore.WHITE+Style.BRIGHT} {explorer} {Style.RESET_ALL}"
            )
            return True
        
        return False
            
    async def process_accounts(self, account: str, address: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(account, address, use_proxy, rotate_proxy)
        if logined:
            proxy = self.get_next_proxy_for_account(address) if use_proxy else None
            
            user = await self.user_info(address, proxy)
            if user and user.get("message") == "SUCCESS":
                points = user.get("result", {}).get("takerPoints", 0)

                balance = f"{float(points):.1f}"

                self.log(
                    f"{Fore.CYAN+Style.BRIGHT}Balance:{Style.RESET_ALL}"
                    f"{Fore.WHITE+Style.BRIGHT} {balance} Opoints {Style.RESET_ALL}"
                )

                self.log(f"{Fore.CYAN+Style.BRIGHT}Mining :{Style.RESET_ALL}")

                first_sign = user.get("result", {}).get("firstSign", False)
                if first_sign:
                    self.log(
                        f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                        f"{Fore.YELLOW+Style.BRIGHT}Solving Cf Turnstile...{Style.RESET_ALL}"
                    )

                    turnstile_token = await self.solve_cf_turnstile(proxy)
                    if turnstile_token:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Message :{Style.RESET_ALL}"
                            f"{Fore.GREEN+Style.BRIGHT} Cf Turnstile Solved Successfully {Style.RESET_ALL}"
                        )

                        start = await self.start_mining(address, turnstile_token, "true", proxy)
                        if start and start.get("message") == "SUCCESS":
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                f"{Fore.GREEN+Style.BRIGHT} Activated Successfully {Style.RESET_ALL}"
                            )

                    else:
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Message :{Style.RESET_ALL}"
                            f"{Fore.RED+Style.BRIGHT} Cf Turnstile Not Solved {Style.RESET_ALL}"
                        )

                else:
                    next_timestamp = user.get("result", {}).get("nextTimestamp", 0)
                    formatted_timestamp = next_timestamp / 1000

                    if int(time.time()) > formatted_timestamp:
                        is_able = await self.process_activate_mining(account, address, use_proxy)
                        if is_able:
                            self.log(
                                f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                f"{Fore.YELLOW+Style.BRIGHT}Solving Cf Turnstile...{Style.RESET_ALL}"
                            )

                            turnstile_token = await self.solve_cf_turnstile(proxy)
                            if turnstile_token:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                    f"{Fore.BLUE+Style.BRIGHT}Message :{Style.RESET_ALL}"
                                    f"{Fore.GREEN+Style.BRIGHT} Cf Turnstile Solved Successfully {Style.RESET_ALL}"
                                )

                                start = await self.start_mining(address, turnstile_token, "false", proxy)
                                if start and start.get("message") == "SUCCESS":
                                    self.log(
                                        f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                        f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                                        f"{Fore.GREEN+Style.BRIGHT} Activated Successfully {Style.RESET_ALL}"
                                    )

                            else:
                                self.log(
                                    f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                                    f"{Fore.BLUE+Style.BRIGHT}Message :{Style.RESET_ALL}"
                                    f"{Fore.RED+Style.BRIGHT} Cf Turnstile Not Solved {Style.RESET_ALL}"
                                )
                        
                    else:
                        reactived_time_wib = datetime.fromtimestamp(formatted_timestamp).astimezone(wib).strftime('%x %X %Z')
                        self.log(
                            f"{Fore.MAGENTA+Style.BRIGHT} ● {Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT}Status  :{Style.RESET_ALL}"
                            f"{Fore.YELLOW+Style.BRIGHT} Already Activated {Style.RESET_ALL}"
                            f"{Fore.MAGENTA+Style.BRIGHT}-{Style.RESET_ALL}"
                            f"{Fore.BLUE+Style.BRIGHT} Next Activation at {Style.RESET_ALL}"
                            f"{Fore.WHITE+Style.BRIGHT}{reactived_time_wib}{Style.RESET_ALL}"
                        )

    async def main(self):
        try:
            with open('accounts.txt', 'r') as file:
                accounts = [line.strip() for line in file if line.strip()]

            capctha_key = self.load_2captcha_key()
            if capctha_key:
                self.CAPTCHA_KEY = capctha_key
            
            use_proxy_choice, rotate_proxy = self.print_question()

            while True:
                use_proxy = False
                if use_proxy_choice in [1, 2]:
                    use_proxy = True

                self.clear_terminal()
                self.welcome()
                self.log(
                    f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
                )

                if use_proxy:
                    await self.load_proxies(use_proxy_choice)
                
                separator = "=" * 25
                for account in accounts:
                    if account:
                        address = self.generate_address(account)

                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}{separator}[{Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(address)} {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{separator}{Style.RESET_ALL}"
                        )

                        if not address:
                            self.log(
                                f"{Fore.CYAN + Style.BRIGHT}Status    :{Style.RESET_ALL}"
                                f"{Fore.RED + Style.BRIGHT} Invalid Private Key or Library Version Not Supported {Style.RESET_ALL}"
                            )
                            continue

                        await self.process_accounts(account, address, use_proxy, rotate_proxy)
                        await asyncio.sleep(3)

                self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*72)
                seconds = 3 * 60 * 60
                while seconds > 0:
                    formatted_time = self.format_seconds(seconds)
                    print(
                        f"{Fore.CYAN+Style.BRIGHT}[ Wait for{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} {formatted_time} {Style.RESET_ALL}"
                        f"{Fore.CYAN+Style.BRIGHT}... ]{Style.RESET_ALL}"
                        f"{Fore.WHITE+Style.BRIGHT} | {Style.RESET_ALL}"
                        f"{Fore.BLUE+Style.BRIGHT}All Accounts Have Been Processed.{Style.RESET_ALL}",
                        end="\r"
                    )
                    await asyncio.sleep(1)
                    seconds -= 1

        except FileNotFoundError:
            self.log(f"{Fore.RED}File 'accounts.txt' Not Found.{Style.RESET_ALL}")
            return
        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Sowing()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Sowing Taker - BOT{Style.RESET_ALL}                                       "                              
        )

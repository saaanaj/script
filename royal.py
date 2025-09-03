#!/usr/bin/env python3
"""
Royal NFT Website Automation Script
Logs into Royal NFT website and displays dashboard data
"""

import requests
from bs4 import BeautifulSoup, Tag
import json
import sys
from urllib.parse import urljoin
import time
import gzip
import io
import getpass

class RoyalNFTAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://royalnft.club"
        self.login_url = "https://royalnft.club/user/login.php"
        self.login_process_url = "https://royalnft.club/user/process3/login_process.php"
        self.dashboard_url = "https://royalnft.club/user/index.php"
        self.dashboard_alt_url = "https://royalnft.club/user/dashboard.php"
        
        # Username and password will be set during login
        self.username = None
        self.password = None
        
        # Set headers to mimic a real browser but disable compression for debugging
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'identity',  # Disable compression to get plain text
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Cache-Control': 'no-cache'
        })

    def get_credentials(self):
        """Get username and password from user input"""
        print("\n" + "="*50)
        print("🔐 ROYAL NFT LOGIN CREDENTIALS")
        print("="*50)
        
        try:
            # Get username
            self.username = input("👤 Enter Username: ").strip()
            if not self.username:
                print("❌ Username cannot be empty!")
                return False
            
            # Get password (hidden input)
            self.password = getpass.getpass("🔑 Enter Password: ").strip()
            if not self.password:
                print("❌ Password cannot be empty!")
                return False
            
            print(f"✅ Credentials received for user: {self.username}")
            return True
            
        except KeyboardInterrupt:
            print("\n\n⚠️ Input cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Error getting credentials: {e}")
            return False

    def login(self):
        """Login to the Royal NFT website and validate credentials"""
        try:
            print("🔐 Starting login process...")
            
            # Add a delay to appear more human-like
            time.sleep(2)
            
            # Try to get the main page first to establish session properly
            print("🏠 Accessing main page...")
            main_response = self.session.get(self.base_url)
            if main_response.status_code == 200:
                print("✅ Main page accessed successfully")
            else:
                print(f"⚠️ Main page returned status: {main_response.status_code}")
            
            time.sleep(1)
            
            # Now try the login page
            print("🔑 Accessing login page...")
            response = self.session.get(self.login_url)
            if response.status_code != 200:
                print(f"❌ Failed to access login page. Status code: {response.status_code}")
                return False
            
            print("✅ Accessed login page successfully")
            
            # Parse the login page to see what fields are required
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the login form
            login_form = soup.find('form')
            if login_form:
                print("🔍 Analyzing login form...")
                # Find all input fields
                inputs = login_form.find_all('input')
                for inp in inputs:
                    inp_type = inp.get('type', 'text')
                    inp_name = inp.get('name', 'unnamed')
                    inp_value = inp.get('value', '')
                    print(f"   📝 Input: type='{inp_type}', name='{inp_name}', value='{inp_value}'")
            
            # Try simple direct login
            print("🚀 Attempting login...")
            
            # Prepare login data with correct field names and token
            login_data = {
                'userid': self.username,  # The form uses 'userid' not 'username'
                'password': self.password
            }
            
            # Add the CSRF token if found
            if login_form:
                token_input = login_form.find('input', {'name': 'token', 'type': 'hidden'})
                if token_input and token_input.get('value'):
                    login_data['token'] = token_input.get('value')
                    print(f"🔑 Added CSRF token: {token_input.get('value')}")
            
            # Send login request with proper headers
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.login_url,
                'Origin': self.base_url,
                'X-Requested-With': 'XMLHttpRequest'
            }
            
            print(f"📤 Validating credentials for username: {self.username}")
            
            login_response = self.session.post(
                self.login_process_url,
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            print(f"📥 Login response status: {login_response.status_code}")
            print(f"🔗 Final URL after login: {login_response.url}")
            
            # Check if login failed by looking at the response
            if login_response.status_code != 200:
                print("❌ Login failed - Server error")
                return False
            
            # Check if we're still on login page or error page
            if 'login.php' in login_response.url and 'process' not in login_response.url:
                print("❌ Login failed - Invalid username or password")
                return False
            
            # Try to access a protected page to verify login success
            time.sleep(2)
            test_urls = [
                "https://royalnft.club/user/index.php",
                "https://royalnft.club/user/profile.php",
                "https://royalnft.club/user/my_nft.php"
            ]
            
            for test_url in test_urls:
                print(f"🔄 Testing access to: {test_url}")
                test_response = self.session.get(test_url)
                
                if test_response.status_code == 200:
                    # Check if we can access actual content (not redirected to login/register)
                    content = test_response.text.lower()
                    
                    # If we find actual dashboard content, login succeeded
                    if any(keyword in content for keyword in ['balance', 'profit', 'dashboard', 'logout', 'wallet']):
                        print(f"✅ Login successful! Accessing dashboard at: {test_url}")
                        return True
                    elif 'register' in test_response.url or 'login' in test_response.url:
                        continue  # Try next URL
                    else:
                        # Page loads but might be dashboard
                        print(f"✅ Login successful! Dashboard accessible at: {test_url}")
                        return True
            
            # If no protected pages are accessible, login likely failed
            print("❌ Login failed - Unable to access dashboard pages")
            print("⚠️ Please check your username and password")
            return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during login: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during login: {e}")
            return False

    def extract_dashboard_data(self):
        """Extract real dashboard data from accessible pages after successful login"""
        try:
            print("📊 Extracting real dashboard data...")
            
            # URLs to try for data extraction
            test_urls = [
                "https://royalnft.club/user/index.php",
                "https://royalnft.club/user/my_nft.php", 
                "https://royalnft.club/user/withdraw.php",
                "https://royalnft.club/user/profile.php"
            ]
            
            dashboard_data = {
                'user_info': {'greetings': []},
                'financial_data': {},
                'trade_info': '',
                'pages_accessed': 0
            }
            
            # Try to extract real data from accessible pages
            for url in test_urls:
                try:
                    print(f"🔍 Checking: {url}")
                    response = self.session.get(url)
                    
                    if response.status_code == 200:
                        # Decode response content
                        try:
                            content = response.text
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Check if this is actually a dashboard page (not registration)
                            if 'register' not in response.url.lower() and 'login' not in response.url.lower():
                                print(f"✅ Successfully accessed: {url}")
                                dashboard_data['pages_accessed'] += 1
                                
                                # Extract user greeting
                                for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
                                    text = tag.get_text(strip=True)
                                    if 'hello' in text.lower() and text not in dashboard_data['user_info']['greetings']:
                                        dashboard_data['user_info']['greetings'].append(text)
                                        print(f"👤 Found greeting: {text}")
                                
                                # Extract financial data using regex patterns
                                import re
                                page_text = soup.get_text()
                                
                                # Look for financial data patterns
                                financial_patterns = {
                                    'Main Balance': r'main\s+balance[:\s]*\$?([\d,]+(?:\.\d{2})?)',
                                    'Total Profit': r'total\s+profit[:\s]*\$?([\d,]+(?:\.\d{2})?)', 
                                    'Profit From Trades': r'profit\s+from\s+trades[:\s]*\$?([\d,]+(?:\.\d{2})?)',
                                    'Referral Income': r'referral\s+income[:\s]*\$?([\d,]+(?:\.\d{2})?)',
                                    'Direct Team': r'direct\s+team[:\s]*(\d+)',
                                    'My Team': r'my\s+team[:\s]*(\d+)|total\s+team[:\s]*(\d+)',
                                    'Total Business': r'total\s+business[:\s]*\$?([\d,]+(?:\.\d{2})?)',
                                    'Total Deposit': r'total\s+deposit[:\s]*\$?([\d,]+(?:\.\d{2})?)',
                                    'Total Withdraw': r'total\s+withdraw[:\s]*\$?([\d,]+(?:\.\d{2})?)'
                                }
                                
                                for label, pattern in financial_patterns.items():
                                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                                    if matches:
                                        # Take the first non-empty match
                                        value = next((m for m in matches if m), None)
                                        if value:
                                            dashboard_data['financial_data'][label] = value
                                            print(f"💰 Found {label}: {value}")
                                
                                # Look for trade information
                                trade_patterns = [
                                    r'(\d+)\s+trades?\s+(?:are\s+)?completed',
                                    r'(\d+)\s+(?:are\s+)?in\s+progress'
                                ]
                                
                                for pattern in trade_patterns:
                                    matches = re.findall(pattern, page_text, re.IGNORECASE)
                                    if matches:
                                        dashboard_data['trade_info'] += f" {matches[0]} trades found"
                                        print(f"📋 Found trade info: {matches[0]}")
                            else:
                                print(f"⚠️ {url} redirected to: {response.url}")
                                
                        except Exception as e:
                            print(f"⚠️ Error parsing {url}: {e}")
                            continue
                    else:
                        print(f"⚠️ {url} returned status: {response.status_code}")
                        
                except Exception as e:
                    print(f"⚠️ Error accessing {url}: {e}")
                    continue
            
            # If no real user greeting found, use the username
            if not dashboard_data['user_info']['greetings']:
                dashboard_data['user_info']['greetings'] = [f"Hello, {self.username}"]
            
            print(f"✅ Data extraction completed! Accessed {dashboard_data['pages_accessed']} pages")
            return dashboard_data
            
        except Exception as e:
            print(f"❌ Error during data extraction: {e}")
            return None

    def display_data(self, data):
        """Display Royal NFT dashboard data in the exact format provided"""
        if not data:
            print("❌ No data to display")
            return
        
        print("\n" + "="*80)
        print("🏆 ROYAL NFT - DASHBOARD DATA")
        print("="*80)
        
        # Display logo and user greeting
        print("\n👤 USER INFORMATION:")
        print("-"*50)
        print("   🏠 Logo")
        
        # Show actual greetings found or username
        if data.get('user_info', {}).get('greetings'):
            for greeting in data['user_info']['greetings']:
                print(f"   ✅ {greeting}")
        else:
            print(f"   ✅ Hello, {self.username}")
        
        # Show trade information if found
        if data.get('trade_info'):
            print(f"   📋 Trade Status: {data['trade_info']}")
        else:
            print("   📋 Your trades status: No trade information found")
        
        print("\n🛒 PURCHASE NFT:")
        print("-"*50)
        print("   ⚠️ No NFT trades found. Please purchase an NFT to start trading.")
        
        print("\n💰 FINANCIAL SUMMARY:")
        print("-"*50)
        
        # Define financial items to display
        financial_items = [
            ('Main Balance', 'This is total profit for the day\nIt will be credited to your crypto wallet at 11:00 AM'),
            ('Total Profit', 'This is total profit you earned till date\nTrade Profit + Referral Earnings + Rewards'),
            ('Profit From Trades', 'This is total profit you earned till date\nTrade Profit'),
            ('Referral Income', 'This is Referral Income you earned till date\nReferral Income'),
            ('Direct Team', 'This is your direct team till date\nDirect Team'),
            ('My Team', 'This is your total team till date\nTotal Team'),
            ('Total Business', 'This is your total Business till date\nTotal Business'),
            ('Total Deposit', 'This is your total Deposit till date\nTotal Deposit'),
            ('Total Withdraw', 'This is your total Withdraw till date\nTotal Withdraw')
        ]
        
        # Display financial data (real or default)
        for item_name, description in financial_items:
            print(f"\n📊 {item_name}")
            
            # Use real data if available, otherwise show $0 or 0
            if data.get('financial_data') and item_name in data['financial_data']:
                value = data['financial_data'][item_name]
                # Add $ prefix if it's a monetary value and doesn't already have it
                if item_name not in ['Direct Team', 'My Team'] and not value.startswith('$'):
                    value = f"${value}"
                print(f"   Amount: {value}")
                print(f"   💵 REAL DATA EXTRACTED FROM WEBSITE")
            else:
                # Default values
                if item_name in ['Direct Team', 'My Team']:
                    print("   Amount: 0")
                else:
                    print("   Amount: $0")
            
            # Show description
            desc_lines = description.split('\n')
            for line in desc_lines:
                if line.strip():
                    print(f"   📄 {line.strip()}")
        
        print("\n" + "="*80)
        
        # Show summary
        pages_accessed = data.get('pages_accessed', 0)
        real_data_count = len(data.get('financial_data', {}))
        
        if real_data_count > 0:
            print(f"📊 SUMMARY: ✅ {real_data_count} real financial data items extracted from {pages_accessed} pages!")
        else:
            print(f"📊 SUMMARY: Login successful, dashboard template displayed ({pages_accessed} pages checked)")
        
        print("="*80)

    def run(self):
        """Main method to run the automation"""
        print("🚀 Starting Royal NFT Automation Script")
        print("="*50)
        
        # Step 1: Get credentials from user
        if not self.get_credentials():
            print("❌ Failed to get credentials. Exiting...")
            return False
        
        # Step 2: Login
        if not self.login():
            print("❌ Failed to login. Exiting...")
            return False
        
        # Wait a moment before fetching data
        time.sleep(2)
        
        # Step 3: Extract dashboard data
        data = self.extract_dashboard_data()
        
        if data:
            # Step 4: Display the data
            self.display_data(data)
            return True
        else:
            print("❌ Failed to extract dashboard data")
            return False

def main():
    """Main function"""
    try:
        automation = RoyalNFTAutomation()
        success = automation.run()
        
        if success:
            print("\n✅ Automation completed successfully!")
        else:
            print("\n❌ Automation failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

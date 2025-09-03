#!/usr/bin/env python3
"""
Royal NFT Website Automation Script
Logs into Royal NFT website and extracts dashboard data
"""

import requests
from bs4 import BeautifulSoup, Tag
import json
import sys
from urllib.parse import urljoin
import time

class RoyalNFTAutomation:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://royalnft.club"
        self.login_url = "https://royalnft.club/user/login.php"
        self.login_process_url = "https://royalnft.club/user/process3/login_process.php"
        self.dashboard_url = "https://royalnft.club/user/index.php"
        self.dashboard_alt_url = "https://royalnft.club/user/dashboard.php"
        
        # Login credentials from memory
        self.username = "NFT913388"
        self.password = "Kumar@123"
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin'
        })

    def login(self):
        """Login to the Royal NFT website"""
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
            
            # Try simple direct login without parsing form first
            print("🚀 Attempting direct login...")
            
            # Prepare login data
            login_data = {
                'username': self.username,
                'password': self.password
            }
            
            # Send login request with proper headers
            login_headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Referer': self.login_url,
                'Origin': self.base_url,
                'X-Requested-With': 'XMLHttpRequest'  # This might help
            }
            
            print(f"📤 Sending login request with username: {self.username}")
            
            login_response = self.session.post(
                self.login_process_url,
                data=login_data,
                headers=login_headers,
                allow_redirects=True
            )
            
            print(f"📥 Login response status: {login_response.status_code}")
            print(f"🔗 Final URL after login: {login_response.url}")
            
            # Wait a moment after login
            time.sleep(2)
            
            # Try to access dashboard directly to test login success
            print("🔄 Testing dashboard access...")
            dashboard_test = self.session.get(self.dashboard_url)
            
            print(f"📊 Dashboard test status: {dashboard_test.status_code}")
            print(f"🔗 Dashboard test URL: {dashboard_test.url}")
            
            if dashboard_test.status_code == 200:
                # Try to parse the dashboard to see if we're logged in
                try:
                    soup = BeautifulSoup(dashboard_test.text, 'html.parser')
                    title_tag = soup.find('title')
                    page_title = title_tag.text.strip() if title_tag else "No title"
                    print(f"📜 Dashboard page title: {page_title}")
                    
                    # Look for indicators of successful login
                    h2_tag = soup.find('h2')
                    if h2_tag:
                        h2_text = h2_tag.text.strip()
                        print(f"👤 Found H2 text: {h2_text}")
                        
                        if 'hello' in h2_text.lower() or self.username.lower() in h2_text.lower():
                            print("✅ Login successful! Found user greeting.")
                            return True
                    
                    # Look for logout link as another indicator
                    logout_link = soup.find('a', href=lambda x: x and 'logout' in x.lower())
                    if logout_link:
                        print("✅ Login successful! Found logout link.")
                        return True
                    
                    # Look for any user-specific content
                    user_content = soup.find(string=lambda x: x and self.username in x)
                    if user_content:
                        print("✅ Login successful! Found username in page content.")
                        return True
                    
                    # If page loads but no clear indicators, check if it's not a login page
                    if 'login' not in dashboard_test.url.lower() and 'login' not in page_title.lower():
                        print("✅ Login appears successful! Not on login page.")
                        return True
                    
                    print("⚠️ Dashboard accessible but login status unclear")
                    return False
                    
                except Exception as e:
                    print(f"⚠️ Error parsing dashboard: {e}")
                    return False
            else:
                print("❌ Dashboard not accessible - login likely failed")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error during login: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during login: {e}")
            return False

    def extract_dashboard_data(self):
        """Extract dashboard data from the home page"""
        try:
            print("📊 Fetching dashboard data...")
            
            # Try multiple possible dashboard URLs
            dashboard_urls = [
                self.dashboard_url,
                self.dashboard_alt_url,
                "https://royalnft.club/user/",
                "https://royalnft.club/user/home.php",
                "https://royalnft.club/user/register.php"  # Sometimes registration page has data
            ]
            
            response = None
            working_url = None
            
            for url in dashboard_urls:
                try:
                    print(f"🔍 Trying dashboard URL: {url}")
                    test_response = self.session.get(url)
                    
                    if test_response.status_code == 200:
                        # For register.php, we'll still try to extract data
                        if 'register.php' in url or ('register.php' not in test_response.url.lower() and 'login.php' not in test_response.url.lower()):
                            print(f"✅ Found accessible URL: {url} -> {test_response.url}")
                            response = test_response
                            working_url = url
                            break
                        else:
                            print(f"⚠️ URL {url} redirected to {test_response.url}")
                    else:
                        print(f"⚠️ URL {url} returned status {test_response.status_code}")
                except Exception as e:
                    print(f"⚠️ Error accessing {url}: {e}")
                    continue
            
            if not response:
                print("❌ Failed to find a working dashboard URL")
                return None
            
            print(f"📥 Dashboard response status: {response.status_code}")
            print(f"🔗 Dashboard URL: {response.url}")
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Debug: Save dashboard content
            try:
                with open('debug_dashboard.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("💾 Saved dashboard content to debug_dashboard.html")
            except Exception as e:
                print(f"⚠️ Could not save dashboard debug file: {e}")
            
            # Debug: Print page title to verify we're on the right page
            title_tag = soup.find('title')
            page_title = title_tag.text.strip() if title_tag else "No title found"
            print(f"📜 Page title: {page_title}")
            
            # Extract user name
            user_name = "Unknown"
            h2_tag = soup.find('h2')
            if h2_tag and h2_tag.text:
                user_name = h2_tag.text.replace('Hello,', '').strip()
                print(f"👤 Found user name: {user_name}")
            
            # Extract trade information
            trade_info = "No trade information found"
            trade_p = soup.find('p', class_='mb-2')
            if trade_p and trade_p.text:
                trade_info = trade_p.text.strip()
                print(f"📊 Found trade info: {trade_info}")
            
            # Extract all summary card data
            dashboard_data = {
                'user_name': user_name,
                'trade_info': trade_info,
                'financial_data': {}
            }
            
            # Find all summary cards
            summary_cards = soup.find_all('div', class_='summary-card')
            print(f"📋 Found {len(summary_cards)} summary cards")
            
            # If no summary cards found, try alternative selectors
            if not summary_cards:
                print("🔍 Trying alternative card selectors...")
                # Try different possible class names
                alternative_selectors = [
                    'div.card',
                    'div.info-card',
                    'div.balance-card',
                    'div.financial-card',
                    'div[class*="card"]'
                ]
                
                for selector in alternative_selectors:
                    cards = soup.select(selector)
                    if cards:
                        print(f"✅ Found {len(cards)} cards with selector: {selector}")
                        summary_cards = cards
                        break
            
            for i, card in enumerate(summary_cards):
                print(f"📋 Processing card {i+1}...")
                
                # Get the title from fs-4 class or alternatives
                title_div = card.find('div', class_='fs-4')
                if not title_div:
                    # Try alternative title selectors
                    title_div = card.find(['h3', 'h4', 'h5', 'div'], class_=['title', 'card-title', 'header'])
                
                # Get the amount from the amount class or alternatives
                amount_div = card.find('div', class_='amount')
                if not amount_div:
                    # Try alternative amount selectors
                    amount_div = card.find(['div', 'span', 'strong'], class_=['value', 'price', 'balance', 'total'])
                
                if title_div and amount_div:
                    title = title_div.text.strip()
                    amount = amount_div.text.strip()
                    
                    print(f"   ✅ {title}: {amount}")
                    
                    # Also get description if available
                    desc_div = card.find('div', class_='desc')
                    if not desc_div:
                        desc_div = card.find(['div', 'p', 'span'], class_=['description', 'subtitle', 'info'])
                    
                    description = desc_div.text.strip() if desc_div else ""
                    
                    dashboard_data['financial_data'][title] = {
                        'amount': amount,
                        'description': description
                    }
                else:
                    print(f"   ⚠️ Card {i+1}: Could not extract title or amount")
            
            # If we still have no financial data, try to extract any numerical values
            if not dashboard_data['financial_data']:
                print("🔍 No cards found, trying to extract any financial data...")
                # Look for any elements with currency symbols or numbers
                import re
                text_content = soup.get_text()
                # Find patterns like $123.45, ₹1000, 1,234.56, etc.
                money_patterns = re.findall(r'[₹$€£¥]?[\d,]+\.?\d*', text_content)
                if money_patterns:
                    print(f"💰 Found potential financial values: {money_patterns[:10]}...")  # Show first 10
            
            print("✅ Dashboard data extracted successfully!")
            return dashboard_data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error while fetching dashboard: {e}")
            return None
        except Exception as e:
            print(f"❌ Error parsing dashboard data: {e}")
            return None

    def display_data(self, data):
        """Display the extracted data in a formatted way"""
        if not data:
            print("❌ No data to display")
            return
        
        print("\n" + "="*60)
        print("🏆 ROYAL NFT DASHBOARD DATA")
        print("="*60)
        
        print(f"👤 User: {data['user_name']}")
        print(f"📈 Trade Status: {data['trade_info']}")
        
        print("\n💰 FINANCIAL SUMMARY:")
        print("-"*40)
        
        for title, info in data['financial_data'].items():
            print(f"\n📊 {title}")
            print(f"   Amount: {info['amount']}")
            if info['description']:
                # Format description for better readability
                desc_lines = info['description'].replace('<br>', '\n').split('\n')
                for line in desc_lines:
                    if line.strip():
                        print(f"   {line.strip()}")
        
        print("\n" + "="*60)

    def run(self):
        """Main method to run the automation"""
        print("🚀 Starting Royal NFT Automation Script")
        print("="*50)
        
        # Step 1: Login
        if not self.login():
            print("❌ Failed to login. Exiting...")
            return False
        
        # Wait a moment before fetching data
        time.sleep(2)
        
        # Step 2: Extract dashboard data
        data = self.extract_dashboard_data()
        
        if data:
            # Step 3: Display the data
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
        print("\n\n⚠️  Script interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

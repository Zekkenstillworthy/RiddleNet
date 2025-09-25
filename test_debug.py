#!/usr/bin/env python3
"""
Script to test the debug logging by making requests to both simulation pages
"""

import requests
import time

def main():
    base_url = "http://127.0.0.1:5001"
    
    # Session cookies from terminal output - these will be used to authenticate
    cookies = {
        'session': '.eJw9zjuOwzAMhOG7qN5C0pAyncsYJEUhKWwEflSLvXtcLNLO_MX3m5axx_FMj3O_4ictr54eCewq4hliFBwGK1F75kmlC8ps1Z0ppj5yOHiUuUhhDQDkmQyzUmmKyGroMDfrFIhC3ipXphw9K4aStAlqdUxDeAgaQYa0dEPesa-6xXZ-adcR-7_vDvQ6n8umaxxv9bhH7etru49vVv4-ST1CkA.aMWA7Q.bHPpdw7dUKIRk39NqJOxpp6ZXBU',
        'admin_session': '.eJwtkMFuwyAQRH8Fccklimwv2MSXHtp-RRVZCywJkg0umFZVlH8vTnua2dFo9TR3PrkZ840yHz_unG1VOKUUEz_y913ZHNH6cGXZL2XGzccwstdYZstC3JguvrqSZuZql4Jdow8bO6RA2_Tl6ZvSaZfpGTg_0-HE3rxlP7GwhTCww2ehvL-drimW9a_9tBOu_sB8yBuhfeGXx-VYcRPlGx8dzpnq6S0fOUiDSpkGlBYkSYNuqbONHFBZBe1Zd8ZIQYN1DRmQrj23qpVIACBMIzScUbQ9AjWowYI2WltBQK0wfSc7KRqyDYJDofoBUHducEo6Bb0A5VRft5pWSgsGCnXBLZUdrWRK_3y1gGW7TQEXyisaqiHaxQf--AVWX36S.aNQjVw.EzdoqPLwwvcaY00TSBRofQgGA_A',
        'user_session': '.eJw9T8tqwzAQ_BWhcw6SV5LX_pNSgtldreKCG5fIKpSQf49CS0_DPBhm7nYpG9VVq53f79YcHWxtIlqrPdm3vZmVvtWw6tVs--Wi2eztMH-R0rbtx54f51PvuWld7Vxoq9rpR7azhSiEKA6Qg0ZlYK9DdnEkzAh-4kEkBh1zcSoQi588-kgKAEFcYJgo-ESgjhgysDDnoKA-SBriEIPT7AgKBUwjEA9lLBgLQgqABVO_sLSqt981vlNqx7pc6VPrF4l28WV3_T_lH086OlUc.aNQtPA.6_wS3vpi--Fw7VOzTluRSwr_01w'
    }
    
    print("Testing debug logging for simulation pages...")
    
    # Test 1: User simulation page
    print("\n1. Requesting user simulation page: /dynamic/simulation/1")
    try:
        response = requests.get(f"{base_url}/dynamic/simulation/1", cookies=cookies, timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ User simulation page loaded successfully")
        else:
            print(f"   ❌ Failed to load user simulation page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error requesting user simulation page: {e}")
    
    # Wait a moment
    time.sleep(2)
    
    # Test 2: Admin simulation edit page
    print("\n2. Requesting admin simulation edit page: /admin/simulation/edit/1")
    try:
        response = requests.get(f"{base_url}/admin/simulation/edit/1", cookies=cookies, timeout=10)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Admin simulation edit page loaded successfully")
        else:
            print(f"   ❌ Failed to load admin simulation edit page: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error requesting admin simulation edit page: {e}")
    
    print("\n3. Checking for debug log file...")
    import os
    log_file = "debug_device_counts.log"
    if os.path.exists(log_file):
        print(f"   ✅ Debug log file found: {log_file}")
        with open(log_file, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"   📄 Log content:")
            print(content)
    else:
        print(f"   ❌ Debug log file not found: {log_file}")

if __name__ == "__main__":
    main()
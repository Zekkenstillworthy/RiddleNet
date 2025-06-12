import requests
import json

# Test the main networking endpoint that was causing 500 errors
test_urls = [
    'http://localhost:5000/api/networking/lesson/1.1',
    'http://localhost:5000/api/networking1/lesson/1.1', 
    'http://localhost:5000/api/networking2/lesson/net2_1.1'
]

print("Testing API endpoints after fixes...")
print("=" * 50)

for url in test_urls:
    try:
        print(f'Testing: {url}')
        response = requests.get(url, timeout=5)
        print(f'Status Code: {response.status_code}')
        if response.status_code == 200:
            data = response.json()
            print(f'Response keys: {list(data.keys())}')
            if 'title' in data:
                print(f'Title: {data["title"][:50]}...')
            if 'content' in data:
                print(f'Content length: {len(data["content"])} chars')
        else:
            print(f'Error: {response.text}')
        print('-' * 30)
    except requests.exceptions.ConnectionError:
        print(f'Connection failed - server may not be running')
        print('Need to start the Flask server first')
        print('-' * 30)
        break
    except Exception as e:
        print(f'Error: {e}')
        print('-' * 30)

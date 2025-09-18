import requests

try:
    response = requests.get('http://127.0.0.1:5001/questions')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        content = response.text
        print(f'Content length: {len(content)}')
        if 'questions' in content.lower():
            print('✅ Questions data found in response')
        else:
            print('❌ No questions data found')
except Exception as e:
    print(f'Error: {e}')
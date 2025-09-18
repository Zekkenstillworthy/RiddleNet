import requests

try:
    response = requests.get('http://127.0.0.1:5001/questions')
    print(f'Status: {response.status_code}')
    if response.status_code == 200:
        content = response.text
        print(f'Content length: {len(content)}')
        # Look for specific HTML elements
        if '<div' in content:
            print('✅ HTML content found')
        if 'question' in content.lower():
            print('✅ Question text found (lowercase)')
        if 'What does' in content:
            print('✅ Question content found')
        if 'riddle' in content.lower():
            print('✅ Category content found')
        
        # Show first 500 chars
        print(f'First 500 chars: {content[:500]}')
except Exception as e:
    print(f'Error: {e}')
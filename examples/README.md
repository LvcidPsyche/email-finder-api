# API Client Examples

This directory contains example client implementations in multiple languages.

## Available Examples

### Python (`python_client.py`)
- Object-oriented client class
- Type hints for better IDE support
- Error handling with requests library
- Usage examples included

**Installation:**
```bash
pip install requests
```

**Usage:**
```python
from python_client import EmailFinderClient

client = EmailFinderClient(api_key="your_key_here")
result = client.find_email("example.com", "John", "Doe")
```

### JavaScript/Node.js (`javascript_client.js`)
- Modern async/await syntax
- Fetch API for HTTP requests
- Works in Node.js and browsers
- CommonJS module export

**Usage:**
```javascript
const EmailFinderClient = require('./javascript_client');

const client = new EmailFinderClient('your_key_here');
const result = await client.findEmail('example.com', 'John', 'Doe');
```

### cURL (`curl_examples.sh`)
- Bash script with all endpoint examples
- Easy to copy/paste individual commands
- Great for quick testing

**Usage:**
```bash
# Edit API_KEY in the script first
./curl_examples.sh
```

## Quick Start

1. Get your API key from the dashboard
2. Choose your language
3. Copy the example code
4. Replace `your_api_key_here` with your actual key
5. Update `base_url` to your actual API URL

## Support

For more examples and documentation:
- API Docs: https://yourapi.com/docs
- GitHub: https://github.com/yourusername/email-finder-api
- Support: support@yourapi.com

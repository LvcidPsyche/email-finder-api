/**
 * JavaScript/Node.js client example for Email Finder API
 */

class EmailFinderClient {
    constructor(apiKey, baseUrl = 'https://api.example.com') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'X-API-Key': apiKey,
            'Content-Type': 'application/json'
        };
    }

    async findEmail(domain, firstName, lastName) {
        const response = await fetch(`${this.baseUrl}/api/find-email`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                domain,
                first_name: firstName,
                last_name: lastName
            })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async verifyEmail(email) {
        const response = await fetch(`${this.baseUrl}/api/verify-email`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ email })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async verifyDomain(domain) {
        const response = await fetch(`${this.baseUrl}/api/verify-domain`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ domain })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async bulkFind(domain, names) {
        const response = await fetch(`${this.baseUrl}/api/bulk-find`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({ domain, names })
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }

    async getUsage() {
        const response = await fetch(`${this.baseUrl}/api/usage`, {
            method: 'GET',
            headers: this.headers
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }

        return response.json();
    }
}

// Example usage
async function main() {
    const client = new EmailFinderClient('your_api_key_here');

    // Find email
    const result = await client.findEmail('example.com', 'John', 'Doe');
    console.log('Found emails:', result.emails);

    // Verify email
    const verification = await client.verifyEmail('john.doe@example.com');
    console.log('Email deliverable:', verification.deliverable);

    // Check usage
    const usage = await client.getUsage();
    console.log(`Requests: ${usage.total_calls}/${usage.rate_limit}`);
}

// Run example
if (require.main === module) {
    main().catch(console.error);
}

module.exports = EmailFinderClient;

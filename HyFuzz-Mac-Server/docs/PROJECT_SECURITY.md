# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in HyFuzz, please report it by emailing **security@hyfuzz.example.com** or by creating a private security advisory on GitHub.

**Please do NOT create public issues for security vulnerabilities.**

We will acknowledge your report within 48 hours and provide a detailed response within 7 days.

---

## Security Considerations

### 1. Authentication & JWT Tokens

#### Current Implementation
The project currently includes a **demonstration JWT implementation** in `src/auth/jwt_handler.py`. This is marked as "not secure, for demonstration only."

#### Recommendations for Production

**HIGH PRIORITY**: Replace the custom JWT implementation with the industry-standard PyJWT library:

```bash
pip install PyJWT
```

```python
# Recommended production implementation
import jwt
import os
from datetime import datetime, timedelta

JWT_SECRET = os.getenv("JWT_SECRET")
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable must be set")

def create_token(payload: dict) -> str:
    payload["exp"] = datetime.utcnow() + timedelta(hours=24)
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
```

#### JWT Secret Configuration

**CRITICAL**: Never use hardcoded JWT secrets in production!

1. **Generate a strong secret:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Set environment variable:**
   ```bash
   export JWT_SECRET="your-generated-secret-here"
   ```

3. **Update `.env` file:**
   ```bash
   JWT_SECRET=your-generated-secret-here
   ```

---

### 2. SQL Injection Prevention

#### Fixed Issues
✅ SQL injection vulnerability in `sqlite_manager.py` has been fixed with table name allowlist validation.

#### Current Protection
- Table names are validated against a whitelist: `ALLOWED_TABLES`
- Query parameters use proper parameterization with `?` placeholders
- Values are never directly interpolated into SQL strings

#### Adding New Tables
To add a new table to the allowlist, update `ALLOWED_TABLES` in `HyFuzz-Ubuntu-Client/src/storage/sqlite_manager.py`:

```python
ALLOWED_TABLES = frozenset({
    "demo",
    "payloads",
    "results",
    "campaigns",
    "executions",
    "defense_verdicts",
    "instrumentation_data",
    "your_new_table",  # Add here
})
```

---

### 3. Pickle Serialization Security

#### Understanding Pickle Risks
Pickle can execute arbitrary code during deserialization. **Never unpickle data from untrusted sources!**

#### Current Usage (Safe)
HyFuzz uses pickle only for:
- ✅ Internal knowledge graph caching (CWE/CVE)
- ✅ LLM response caching (internally generated)
- ✅ Application-controlled cache directories
- ✅ No external/user data deserialization

#### Security Documentation
Security notes have been added to:
- `src/knowledge/graph_cache.py`
- `src/llm/cache_manager.py`

#### Alternative for External Data
For data from external sources, use JSON or msgpack:

```python
import json
import msgpack

# For simple data structures - use JSON
with open("data.json", "w") as f:
    json.dump(data, f)

# For complex/binary data - use msgpack
with open("data.msgpack", "wb") as f:
    msgpack.pack(data, f)
```

---

### 4. Exception Handling

#### Fixed Issues
✅ All bare `except:` clauses have been replaced with specific exception types.

#### Best Practices

**Bad:**
```python
try:
    risky_operation()
except:  # Catches EVERYTHING including KeyboardInterrupt!
    pass
```

**Good:**
```python
try:
    risky_operation()
except (ValueError, KeyError, IOError) as e:
    logger.error(f"Operation failed: {e}")
    # Handle specific exceptions appropriately
```

---

### 5. Environment Variables & Secrets

#### Critical Environment Variables

**Required for Production:**
```bash
# JWT Authentication
JWT_SECRET=<generate-with-secrets.token_urlsafe(32)>

# Database
DATABASE_URL=postgresql://user:password@host/db

# LLM API Keys (if using cloud providers)
OPENAI_API_KEY=<your-api-key>
# or
ANTHROPIC_API_KEY=<your-api-key>
```

#### Best Practices

1. **Never commit `.env` files** - they're in `.gitignore`
2. **Use `.env.example`** for documentation
3. **Rotate secrets regularly** (at least quarterly)
4. **Use secret management tools** in production:
   - AWS Secrets Manager
   - HashiCorp Vault
   - Azure Key Vault
   - Google Secret Manager

#### Checking for Hardcoded Secrets

```bash
# Use tools to scan for secrets
pip install detect-secrets
detect-secrets scan

# Use git-secrets to prevent commits
git secrets --scan
```

---

### 6. Network Security

#### HTTPS Configuration

**Production deployments MUST use HTTPS!**

Update `.env`:
```bash
ENABLE_HTTPS=true
SSL_CERT_FILE=certs/server.crt
SSL_KEY_FILE=certs/server.key
```

#### Generate Self-Signed Certificate (Development Only)
```bash
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
```

#### CORS Configuration

Restrict CORS origins in production:
```bash
CORS_ENABLED=true
CORS_ORIGINS=https://your-production-domain.com
```

---

### 7. Input Validation

#### Implemented Validations
- ✅ Table name allowlist (SQL injection prevention)
- ✅ Type hints and Pydantic models for data validation
- ✅ Protocol-specific payload validation

#### Best Practices

Always validate user input:

```python
from pydantic import BaseModel, validator

class CampaignConfig(BaseModel):
    name: str
    protocol: str
    target: str

    @validator('protocol')
    def validate_protocol(cls, v):
        allowed = {'coap', 'modbus', 'mqtt', 'http'}
        if v not in allowed:
            raise ValueError(f'Protocol must be one of {allowed}')
        return v
```

---

### 8. Dependency Security

#### Regular Audits

```bash
# Check for known vulnerabilities
pip-audit

# Or use safety
pip install safety
safety check -r requirements.txt

# Update dependencies
pip list --outdated
```

#### Automated Scanning

The project uses GitHub's Dependabot for automated dependency updates and security alerts.

#### Version Pinning

Consider using exact versions or upper bounds:
```
requests>=2.31.0,<3.0.0  # Recommended
requests==2.31.0         # Strict (less flexible)
requests>=2.31.0         # Too loose (can break)
```

---

### 9. Logging & Monitoring

#### Sensitive Data in Logs

**Never log:**
- Passwords or password hashes
- JWT tokens
- API keys
- Session tokens
- Personal Identifiable Information (PII)

**Example:**
```python
# Bad
logger.info(f"User logged in with password: {password}")

# Good
logger.info(f"User {username} logged in successfully")
```

#### Log Levels

- **DEBUG**: Development only, may contain sensitive data
- **INFO**: General application flow
- **WARNING**: Unexpected but handled situations
- **ERROR**: Errors that need attention
- **CRITICAL**: System-critical failures

---

### 10. File Permissions

#### Cache Directories

Ensure proper permissions:
```bash
chmod 700 data/knowledge_cache/
chmod 700 data/llm_cache/
```

#### Configuration Files
```bash
chmod 600 .env
chmod 600 config/production.yaml
```

---

## Security Checklist for Production

Before deploying to production, ensure:

- [ ] **JWT_SECRET** is set to a strong random value
- [ ] **HTTPS** is enabled with valid certificates
- [ ] **CORS** origins are restricted to known domains
- [ ] **.env** file is NOT committed to version control
- [ ] **Database credentials** are secure and rotated
- [ ] **API keys** are stored in secret management system
- [ ] **Dependency audit** completed (`pip-audit`)
- [ ] **File permissions** are restrictive (700 for dirs, 600 for secrets)
- [ ] **Logging** does not expose sensitive data
- [ ] **Input validation** is in place for all user inputs
- [ ] **Error messages** don't reveal system internals
- [ ] **Rate limiting** is configured for APIs
- [ ] **Backup strategy** is in place
- [ ] **Monitoring & alerting** is configured
- [ ] **Security headers** are set (CSP, HSTS, etc.)

---

## Known Issues & Limitations

### Demonstration Components

The following components are for **demonstration/development only** and should be replaced in production:

1. **Custom JWT Handler** (`src/auth/jwt_handler.py`)
   - Replace with PyJWT library
   - Use strong secret from environment

2. **Default Secrets** (`src/auth/authenticator.py`)
   - Falls back to development secret if JWT_SECRET not set
   - Emits warning but still allows operation
   - **Production must set JWT_SECRET**

---

## Security Response Timeline

| Severity | Initial Response | Fix Timeline |
|----------|-----------------|--------------|
| Critical | 24 hours | 7 days |
| High | 48 hours | 30 days |
| Medium | 1 week | 90 days |
| Low | 2 weeks | Best effort |

---

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

## Contact

For security-related questions or concerns:
- **Email**: security@hyfuzz.example.com
- **GitHub Security Advisories**: [Create Private Advisory](https://github.com/your-org/HyFuzz/security/advisories/new)

---

**Last Updated**: 2025-11-04
**Version**: 1.0.0

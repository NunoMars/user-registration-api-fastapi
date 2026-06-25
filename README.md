
# User Registration API

A production-oriented FastAPI API for user registration and account activation using a 4-digit email verification code.

The project is built with:

* Python
* FastAPI
* PostgreSQL
* asyncpg
* Docker Compose
* pytest

No ORM is used. All database access is implemented with explicit SQL queries through asyncpg.

## Features

* Register a user with an email and password
* Store passwords using Argon2 hashing
* Generate a 4-digit activation code
* Store activation codes as hashes, not in clear text
* Send activation codes through an email provider abstraction
* Use a fake email provider for local execution
* Activate an account with Basic Auth and the received code
* Enforce a 1-minute activation code expiration
* Limit wrong activation attempts
* Return consistent JSON error responses
* Run the API and tests with Docker Compose

## Architecture

The application follows a simple layered architecture:

```text
Client
  -> FastAPI router
  -> User service
  -> User repository
  -> PostgreSQL

User service
  -> Email client abstraction
  -> Fake third-party email provider
```

More details are available in [`architecture.md`](https://chatgpt.com/c/architecture.md).

## Requirements

You only need:

* Docker
* Docker Compose

No local Python installation is required.

## Run the API

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Readiness check:

```bash
curl http://localhost:8000/ready
```

Interactive API documentation:

```text
http://localhost:8000/docs
```

## Run tests

```bash
docker compose run --rm api pytest
```

Expected result:

```text
11 passed
```

## API endpoints

### Register user

```http
POST /api/v1/users/register
Content-Type: application/json
```

Request:

```json
{
  "email": "user@example.com",
  "password": "Secret123!"
}
```

Response:

```json
{
  "id": "11635833-c564-45a8-9b36-7ce030779490",
  "email": "user@example.com",
  "is_active": false
}
```

When the fake email provider is enabled, the activation code is printed in the API logs:

```text
[FAKE EMAIL] To: user@example.com | Activation code: 1234
```

### Activate user

```http
POST /api/v1/users/activate
Authorization: Basic base64(email:password)
Content-Type: application/json
```

Request:

```json
{
  "code": "1234"
}
```

Response:

```json
{
  "id": "11635833-c564-45a8-9b36-7ce030779490",
  "email": "user@example.com",
  "is_active": true
}
```

## PowerShell examples

### Register

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/users/register `
  -ContentType "application/json" `
  -Body '{"email":"user@example.com","password":"Secret123!"}'
```

Then read the activation code from the API logs:

```powershell
docker compose logs api --tail=20
```

### Activate

```powershell
$email = "user@example.com"
$password = "Secret123!"
$pair = "$email`:$password"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [Convert]::ToBase64String($bytes)
$headers = @{ Authorization = "Basic $base64" }

Invoke-RestMethod `
  -Method Post `
  -Uri http://localhost:8000/api/v1/users/activate `
  -Headers $headers `
  -ContentType "application/json" `
  -Body '{"code":"1234"}'
```

## Configuration

The application reads configuration from environment variables.

Example:

```env
APP_ENV=local
DATABASE_URL=postgresql://app:app@postgres:5432/registration
EMAIL_PROVIDER_MODE=fake
APPLY_SCHEMA_ON_STARTUP=true
ACTIVATION_CODE_PEPPER=local-dev-activation-code-pepper
```

Only `.env.example` is committed. Local `.env` files are ignored.

## Email provider

Email sending is implemented behind an abstraction.

For this assignment, the fake provider prints the activation code in the API logs.

This keeps the implementation simple while preserving the design of an external third-party email provider.

## Security notes

* Passwords are hashed with Argon2.
* Activation codes are never stored in clear text.
* Activation code hashes include the user id and an application pepper.
* Activation codes expire after 60 seconds.
* Wrong activation attempts are limited.
* Basic Auth is used only for the activation endpoint, as requested by the assignment.

## Error format

Errors follow this structure:

```json
{
  "error": {
    "code": "USER_ALREADY_EXISTS",
    "message": "A user with this email already exists."
  }
}
```

Examples:

* `USER_ALREADY_EXISTS`
* `INVALID_CREDENTIALS`
* `USER_ALREADY_ACTIVE`
* `INVALID_OR_EXPIRED_ACTIVATION_CODE`
* `TOO_MANY_ACTIVATION_ATTEMPTS`

## Database

The application uses PostgreSQL.

Main tables:

* `users`
* `activation_codes`

The schema is defined in:

```text
app/db/schema.sql
```

For local and test usage, the schema can be applied automatically at startup through:

```env
APPLY_SCHEMA_ON_STARTUP=true
```

## Tests

Current coverage includes:

* health endpoint
* readiness endpoint
* successful registration
* duplicate email conflict
* weak password validation
* successful activation
* wrong password rejection
* wrong code rejection
* expired code rejection
* already active user rejection
* too many activation attempts

## Production improvements

Possible improvements for a real production deployment:

* real third-party email provider integration
* rate limiting per IP and per email
* structured JSON logging
* metrics and tracing
* dedicated migration tooling
* CI pipeline
* secret management
* outbox pattern for email delivery
* stronger abuse protection

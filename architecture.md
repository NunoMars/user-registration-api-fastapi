### Architecture

# Architecture

## Overview

This project is a production-oriented FastAPI API for user registration and account activation.

The application follows a simple layered architecture:

* **API layer** : FastAPI routers, request validation and response models.
* **Service layer** : business rules for registration and activation.
* **Repository layer** : explicit PostgreSQL queries using asyncpg.
* **Email layer** : abstraction for a third-party email provider.
* **Database layer** : PostgreSQL connection pool and SQL schema.

The goal is to keep the implementation simple, testable and close to production practices without adding unnecessary infrastructure.

No ORM is used.

## High-level architecture

```text
Client
  |
  v
FastAPI application
  |
  v
User router
  |
  v
User service
  |-----------------------> Email client abstraction
  |                              |
  |                              v
  |                        Fake email provider
  |
  v
User repository
  |
  v
PostgreSQL
```

## Layers

### API layer

The API layer exposes HTTP endpoints through FastAPI.

Responsibilities:

* receive HTTP requests
* validate request bodies with Pydantic models
* inject dependencies with FastAPI `Depends`
* return typed response models
* convert domain errors into consistent HTTP responses

Main files:

```text
app/users/router.py
app/users/schemas.py
app/main.py
```

### Service layer

The service layer contains business logic.

Responsibilities:

* register a user
* hash user passwords
* generate 4-digit activation codes
* hash activation codes before storage
* enforce activation code expiration
* verify Basic Auth credentials during activation
* limit wrong activation attempts
* activate the account once the code is valid

Main file:

```text
app/users/service.py
```

### Repository layer

The repository layer is responsible for database access.

Responsibilities:

* execute explicit SQL queries
* create users
* retrieve users by email
* create activation codes
* update activation attempts
* mark activation codes as used
* activate users

No ORM is used. Database access is implemented with asyncpg.

Main files:

```text
app/users/repository.py
app/users/records.py
```

### Email layer

The email layer abstracts email delivery.

For this assignment, the implementation uses a fake email provider that prints the activation code in the API logs.

This keeps the API designed as if email delivery were handled by a third-party HTTP service, while keeping the local setup simple.

Main files:

```text
app/email/client.py
app/email/fake_client.py
```

### Database layer

The database layer manages PostgreSQL access and schema initialization.

Responsibilities:

* create the asyncpg connection pool
* close the connection pool on shutdown
* expose database dependencies
* define the SQL schema
* apply the schema in local and test environments

Main files:

```text
app/db/pool.py
app/db/schema.sql
app/db/schema_loader.py
```

## Database schema

The database is PostgreSQL.

### users table

```text
users
  id UUID PRIMARY KEY
  email TEXT UNIQUE
  password_hash TEXT
  is_active BOOLEAN
  created_at TIMESTAMPTZ
  activated_at TIMESTAMPTZ NULL
```

The email uniqueness is enforced using a case-insensitive unique index on `lower(email)`.

### activation_codes table

```text
activation_codes
  id UUID PRIMARY KEY
  user_id UUID REFERENCES users(id)
  code_hash TEXT
  expires_at TIMESTAMPTZ
  used_at TIMESTAMPTZ NULL
  attempts INTEGER
  created_at TIMESTAMPTZ
```

Activation codes are never stored in clear text.

## Registration flow

```text
Client
  |
  | POST /api/v1/users/register
  | { email, password }
  v
User router
  |
  v
User service
  |
  | check if user already exists
  | hash password
  | create inactive user
  | generate 4-digit activation code
  | hash activation code
  | store activation code with 60-second expiration
  v
User repository
  |
  v
PostgreSQL

User service
  |
  | send activation code
  v
Fake email provider
```

## Activation flow

```text
Client
  |
  | POST /api/v1/users/activate
  | Basic Auth: email + password
  | { code }
  v
User router
  |
  v
User service
  |
  | verify Basic Auth credentials
  | check user is not already active
  | retrieve latest unused activation code
  | check expiration
  | verify activation code hash
  | mark activation code as used
  | activate user
  v
User repository
  |
  v
PostgreSQL
```

## Error handling

Domain errors are represented as custom exceptions and converted into consistent JSON responses.

Example:

```json
{
  "error": {
    "code": "USER_ALREADY_EXISTS",
    "message": "A user with this email already exists."
  }
}
```

Main error codes:

* `USER_ALREADY_EXISTS`
* `INVALID_CREDENTIALS`
* `USER_ALREADY_ACTIVE`
* `INVALID_OR_EXPIRED_ACTIVATION_CODE`
* `TOO_MANY_ACTIVATION_ATTEMPTS`

## Technical choices

* FastAPI for the HTTP API.
* asyncpg for asynchronous PostgreSQL access.
* PostgreSQL instead of SQLite.
* Explicit SQL queries instead of an ORM.
* Pydantic for request and response validation.
* FastAPI `Depends` for dependency injection.
* FastAPI lifespan for startup and shutdown.
* Argon2 for password hashing.
* HMAC-SHA256 for activation code hashing.
* Fake email provider behind an abstraction.
* Docker Compose for local execution and tests.
* pytest for automated tests.

## Production improvements

Possible improvements for a real production system:

* rate limiting per IP and per email
* real third-party email provider integration
* structured logging
* metrics and tracing
* stronger abuse protection
* dedicated migration tooling
* secret management
* CI pipeline
* outbox pattern for email delive

## Overview

This project is a production-oriented FastAPI API for user registration and account activation.

The application follows a simple layered architecture:

* **API layer** : FastAPI routers, request validation and response models.
* **Service layer** : business rules for registration and activation.
* **Repository layer** : explicit PostgreSQL queries using asyncpg.
* **Email layer** : abstraction for a third-party email provider.
* **Database layer** : PostgreSQL connection pool and schema.

The goal is to keep the implementation simple, testable and close to production practices without adding unnecessary infrastructure.

## High-level architecture

```text
Client
  |
  v
FastAPI application
  |
  v
User router
  |
  v
User service
  |-----------------------> Email client abstraction
  |                              |
  |                              v
  |                        Fake email provider
  |
  v
User repository
  |
  v
PostgreSQL
```

## Layers

### API layer

The API layer exposes HTTP endpoints through FastAPI.

Responsibilities:

* receive HTTP requests
* validate request bodies with Pydantic models
* inject dependencies with FastAPI `Depends`
* return typed response models
* convert domain errors into consistent HTTP responses

### Service layer

The service layer contains business logic.

Responsibilities:

* register a user
* hash user passwords
* generate 4-digit activation codes
* hash activation codes before storage
* enforce activation code expiration
* verify Basic Auth credentials during activation
* activate the account once the code is valid

### Repository layer

The repository layer is responsible for database access.

Responsibilities:

* execute explicit SQL queries
* create users
* retrieve users by email
* create activation codes
* update activation attempts
* mark activation codes as used
* activate users

No ORM is used. Database access is implemented with asyncpg.

### Email layer

The email layer abstracts email delivery.

For this assignment, the implementation uses a fake email provider that logs or prints the activation code.

This keeps the API designed as if email delivery were handled by a third-party HTTP service, while keeping the local setup simple.

## Database

The database is PostgreSQL.

Main tables:

```text
users
  id
  email
  password_hash
  is_active
  created_at
  activated_at

activation_codes
  id
  user_id
  code_hash
  expires_at
  used_at
  attempts
  created_at
```

Activation codes are not stored in clear text.

## Registration flow

```text
Client
  |
  | POST /api/v1/users/register
  v
FastAPI router
  |
  v
User service
  |
  | validate email and password
  | hash password
  | create inactive user
  | generate 4-digit activation code
  | hash activation code
  | store activation code with 1-minute expiration
  v
Repository / PostgreSQL
  |
  v
Email client
  |
  | send activation code
  v
Fake email provider
```

## Activation flow

```text
Client
  |
  | POST /api/v1/users/activate
  | Authorization: Basic email:password
  | Body: activation code
  v
FastAPI router
  |
  v
User service
  |
  | verify Basic Auth credentials
  | retrieve latest unused activation code
  | check expiration
  | verify activation code
  | mark code as used
  | activate user
  v
Repository / PostgreSQL
```

## Technical choices

* FastAPI for the HTTP API.
* asyncpg for asynchronous PostgreSQL access.
* PostgreSQL instead of SQLite.
* Pydantic for validation and response models.
* FastAPI `Depends` for dependency injection.
* FastAPI lifespan for startup and shutdown.
* Fake email provider behind an abstraction.
* Docker Compose for local execution and tests.

## Production improvements

Possible improvements for a real production system:

* rate limiting per IP and per email
* real third-party email provider integration
* structured logging
* metrics and tracing
* stronger abuse protection
* dedicated migration tooling
* secret management
* CI pipeline

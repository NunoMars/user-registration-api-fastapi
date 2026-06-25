### Architecture

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

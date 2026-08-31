# Week 4

## Goals
- Understand modern web authentication, JSON Web Tokens (JWTs), and Identity Providers (Supabase Auth).
- Implement secure Sign Up, Log In, and Log Out endpoints in FastAPI.
- Guard protected endpoints using reusable Bearer token authentication dependencies.
- Configure Swagger UI with interactive Authorize padlock and publish clean documentation.

## Tasks
- [x] **Backend Track: Auth - Login & Protect (Assignment A4)**: Implemented Supabase Auth, JWT verification, reusable Bearer token dependency guard, Swagger UI Bearer security, and full documentation. See `backend/`.
- [ ] **AI Fluency Track**: See `fluency/`.

## Experience Notes

### My Experience
Finally understood how endpoints of Login and Authentication works especially with those JWT tokens and never knew that each user actually gets very long predefined tokens for security. I do build lots of login pages in both backend and frontend but have never really considered how the workflow actually works using Supabase. I've built some apps here and there with supabase but this enlightened me to actually pay more attention to the authentication and security part of a user's account with my application/program.

### Key Takeaways
- **JWT Cryptography**: Understanding that a JSON Web Token is a mathematically signed access pass consisting of Header, Payload, and Signature, rendering tampering impossible.
- **Identity Provider Abstraction**: Leaning on a dedicated IdP (Supabase Auth) for secure password hashing and token issuance rather than rolling custom cryptography.
- **Reusable Dependency Guards**: Enforcing authentication via FastAPI `Depends(get_current_user)` and `HTTPBearer` so all private routes are protected without repetitive code.
- **Stateless vs. Stateful Auth**: Experiencing how stateless Bearer tokens allow servers to authenticate users on every incoming request without maintaining server-side session memory.

## Notes
- Full project code, setup guide, and documentation live in `backend/`.




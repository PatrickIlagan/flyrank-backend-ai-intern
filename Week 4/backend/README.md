# Auth: Login & Protect (FastAPI + Supabase Auth)

A secure authentication API built with **Python 3.11** and **FastAPI**, integrated with **Supabase Auth** as the Identity Provider (IdP) for user management and JSON Web Token (JWT) issuance.

Part of **FlyRank AI Backend Engineering Internship: Week 4 (Assignment A4: Auth - Login & protect)**.

---

## Stages & Checklist
- [ ] **Stage 0: Setup Server & Supabase Client**: Create Supabase project, copy URL and anon key to git-ignored .env, commit .env.example, and initialize Supabase client.
- [ ] **Stage 1: Sign Up & Log In Routes**: Implement POST /auth/signup (201 Created) and POST /auth/login (returns access token).
- [ ] **Stage 2: Public & Unverified Protected Route**: Implement GET /public/info (200 OK) and GET /protected/profile (returns 401 if Authorization header missing).
- [ ] **Stage 3: Token Verification**: Verify JWT with Supabase Auth (get_user) and return user profile details or 401 on forged/expired tokens.
- [ ] **Stage 4: Auth Middleware & Logout**: Extract reusable FastAPI security dependency (HTTPBearer) and implement POST /auth/logout (204 No Content).
- [ ] **Stage 5: Swagger UI with Bearer Auth**: Configure Swagger UI /docs with the Authorize padlock for token testing.
- [ ] **Stage 6: Publish to GitHub**: Document the setup, verify .env is git-ignored, test clean clone startup, and push.
- [ ] **Stage 7 / Extras (Optional)**: Role-based 403 Forbidden endpoint, token inspection, and AI Rematch diff.

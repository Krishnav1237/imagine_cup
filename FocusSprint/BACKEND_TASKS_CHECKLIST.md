# FocusSprint MVP Backend Tasks

## Database
- [ ] Install PostgreSQL
- [ ] Create database tables: users, content, sprints, sessions, infographics, quizzes
- [ ] Add database indexes

## Authentication
- [ ] Build POST /api/auth/register
- [ ] Build POST /api/auth/login
- [ ] Build GET /api/auth/me
- [ ] Implement JWT tokens
- [ ] Add auth middleware

## YouTube Content Processing
- [ ] Integrate YouTube video downloader (yt-dlp)
- [ ] Connect OpenAI Whisper API for transcription
- [ ] Connect OpenAI GPT-4o for content chunking
- [ ] Build POST /api/content/process endpoint
- [ ] Store sprints in database

## Sprint Sessions
- [ ] Build POST /api/sessions/start endpoint
- [ ] Build POST /api/sessions/complete endpoint
- [ ] Calculate coins earned (base 50 + bonuses)
- [ ] Update user coins in database
- [ ] Track streak multipliers

## Infographic Generation
- [ ] Set up Vertex AI Imagen OR Nano Banana API
- [ ] Build infographic generation service
- [ ] Upload images to S3/Cloud Storage
- [ ] Generate quiz questions with GPT-4o
- [ ] Return infographic + quiz in session completion

## Shop System
- [ ] Build GET /api/shop/items endpoint
- [ ] Build POST /api/shop/purchase endpoint
- [ ] Build GET /api/user/inventory endpoint
- [ ] Seed database with shop items
- [ ] Validate coin balance before purchase

## Frontend Integration
- [ ] Replace mock auth in signup/signin pages
- [ ] Connect upload page to /api/content/process
- [ ] Connect sprint page to session endpoints
- [ ] Display real AI-generated infographics
- [ ] Connect shop page to purchase API

## Deployment
- [ ] Set up production database
- [ ] Set up S3 bucket with CDN
- [ ] Deploy backend to production
- [ ] Configure environment variables
- [ ] Deploy frontend to Vercel

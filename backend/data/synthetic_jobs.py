"""
CortexHire — Synthetic Job Descriptions
5 diverse, rich JDs designed to stress-test the Role Cognition Engine.
Each has hidden needs beyond the obvious keyword list.
"""
from __future__ import annotations

SYNTHETIC_JOBS: list[dict] = [
    {
        "title": "Senior Backend Engineer — Payments Infrastructure",
        "company": "ZetaPay",
        "location": "Bengaluru, India (Hybrid)",
        "employment_type": "full-time",
        "seniority": "senior",
        "description": """
About ZetaPay:
We're a Series B fintech startup processing $2B+ in payments annually for 50,000+ merchants.
We're scaling fast — 3x growth in 18 months — and our infrastructure needs to keep pace.

Role Overview:
We need a Senior Backend Engineer who can own our core payments processing engine.
This isn't a "maintain the system" role. We need someone who can redesign it as we grow.

What You'll Do:
- Architect and build the next-generation payments processing engine
- Design systems that handle 10x our current load without rearchitecting again
- Work directly with the CTO — small team, massive ownership
- Reduce our payment failure rate from 0.8% to <0.1%
- Own incident response for production issues (yes, you'll be paged)

What We Need:
- 4+ years backend engineering experience
- Strong in at least one of: Go, Rust, Java
- Experience with distributed systems, consensus protocols, or messaging queues
- Has built something that handles real money or real-time transactions
- Can debug production fires under pressure

Bonus Points:
- Kafka, Redis, PostgreSQL at scale
- PCI-DSS compliance experience
- Prior startup experience

What We Don't Care About:
- Which college you went to
- Whether you've worked at a FAANG
- Your resume format

What We Do Care About:
- What you've actually built
- How you think under pressure
- Whether you own outcomes, not just tasks

Culture:
Small team (12 engineers), high standards, no bureaucracy.
You'll be one of 3 senior engineers. Your work matters immediately.
        """.strip()
    },
    {
        "title": "ML Engineer — Recommendation Systems",
        "company": "StreamNova",
        "location": "Remote (India preferred)",
        "employment_type": "full-time",
        "seniority": "senior",
        "description": """
StreamNova is a music streaming platform with 80M users across South and Southeast Asia.
We're competing against Spotify and JioSaavn. Our differentiation: hyper-local, cultural relevance.

The Challenge:
Our current recommendation engine is a cosine similarity hack from 2019.
Users churn at 42% monthly — significantly above industry benchmark of 28%.
We believe personalization is the key lever.

Role:
You'll own the recommendation system end-to-end.
This means: research → model development → A/B testing → production deployment → monitoring.

What you need to be able to do:
- Build and ship ML models to production (not just notebooks)
- Design and run A/B experiments with statistical rigor
- Understand user behavior data — funnel analysis, cohort analysis, engagement metrics
- Work with our data engineering team to build the features you need
- Communicate tradeoffs clearly to non-technical stakeholders

Technical Expectations:
- Python + PyTorch or TensorFlow
- Experience with collaborative filtering, content-based, or hybrid recommenders
- Familiarity with feature stores, model serving, and monitoring
- Bonus: Graph neural networks for social recommendation

What success looks like in 6 months:
- Churn reduced from 42% to <30%
- Recommendation click-through rate up by 25%
- A/B test framework live and being used by product team

This is NOT a research role. Papers are nice but shipping is what we reward.
        """.strip()
    },
    {
        "title": "Staff Platform Engineer — Developer Infrastructure",
        "company": "Mosaic Technologies",
        "location": "Hyderabad, India",
        "employment_type": "full-time",
        "seniority": "staff",
        "description": """
Mosaic is a B2B SaaS company with 1,200 engineers across 18 product teams.
We have a developer productivity crisis.

Average time to deploy: 47 minutes.
Average time to set up a new development environment: 3.8 days.
Developer satisfaction score: 3.1/5.

We've hired a Staff Platform Engineer to fix this — potentially you.

Scope of Impact:
You'll build the internal developer platform that 1,200 engineers use every day.
This is multiplier work: make one engineer 10% faster, multiply by 1,200.

What the Role Actually Entails:
- Design, build, and evangelize the internal developer platform (IDP)
- Reduce deploy time from 47 minutes to <10 minutes
- Build golden-path templates for new service creation
- Own the CI/CD infrastructure (currently Jenkins — it needs help)
- Drive adoption — build something engineers actually want to use

Technical Requirements:
- Deep Kubernetes and container orchestration experience
- CI/CD platform design (Jenkins, GitHub Actions, Buildkite, or similar)
- Infrastructure as Code (Terraform required)
- Developer empathy — you've been a developer, you know what pain feels like
- Ability to influence without authority — you'll need to convince teams to change

What Makes Someone Succeed Here:
The last person in this role failed because they could build things but couldn't get adoption.
Technical excellence is necessary but insufficient.
You need to be a platform engineer AND an internal product manager AND a communicator.

Bonus: Experience with Backstage, Port, or similar IDP frameworks.
        """.strip()
    },
    {
        "title": "Founding Full-Stack Engineer",
        "company": "Verdant (Stealth Climate Tech)",
        "location": "Remote (Global)",
        "employment_type": "full-time",
        "seniority": "mid-senior",
        "description": """
Verdant is a stealth-stage climate tech startup backed by top-tier climate investors.
We're building software to help corporations accurately measure, track, and reduce Scope 3 emissions.
The market: $50B+ carbon accounting software market, virtually no good software.

Why This Is Hard:
Scope 3 accounting is complex — supply chain data, emission factors, lifecycle analysis.
The data is messy, the standards are evolving, and enterprises have 10,000-vendor supply chains.
Nobody has solved this well yet. We're going to.

The Role:
You will be engineer #3. There is no separation between frontend and backend here.
You build what needs to exist. You decide the architecture.
You will work directly with the two founders (both have PhDs in climate science, not engineers).

What You Must Have:
- Built a full product before (ideally from 0 to users)
- Comfortable making architectural decisions without a senior engineer above you
- Can work with messy, real-world data
- Python and React — the stack we've started with
- Curiosity about the climate/sustainability domain (we'll teach you the science)

What Will Disqualify You:
- Needing detailed specifications before you can build
- Inability to communicate technical decisions to non-technical founders
- Fear of ambiguity

What You'll Get:
- Meaningful equity (0.5–1.5% depending on experience)
- Work that genuinely matters
- A team that will challenge you intellectually every day

We don't care about your resume's prestige. We care about what you've built and how you think.
        """.strip()
    },
    {
        "title": "Engineering Manager — Growth Engineering",
        "company": "Khata (Series C Fintech)",
        "location": "Mumbai, India",
        "employment_type": "full-time",
        "seniority": "manager",
        "description": """
Khata is a Series C fintech serving 3M small business owners across India.
We help merchants manage their books, collect payments, and access credit.
Our NPS is 78. Our growth is 8% MoM. We're building for 30M.

The Team You'll Lead:
Growth Engineering at Khata isn't marketing automation.
It's the team that rebuilds the product to grow itself — activation, retention, virality, referrals.
You'll lead 8 engineers and 2 data scientists.

What You'll Own:
- Activation: Why do 35% of signups never complete setup? Fix that.
- Retention: Build intelligent re-engagement systems
- Referral engine: Our merchants have networks — we're not using them
- Experimentation platform: We run 20+ A/B tests per month with no proper framework

What You Need:
Experience as an Engineering Manager (2+ years), not just a senior IC.
Track record of improving product metrics, not just shipping features.
Strong data intuition — you read dashboards, you ask questions, you make hypotheses.
Ability to hire, grow, and sometimes let go of people.

The Ideal Candidate Has:
- Led a growth engineering or product engineering team
- Experience at a consumer-facing product with millions of users
- Can write code when needed (you'll need to review PRs and sometimes pair)
- Has shipped features that measurably moved retention or activation

Culture Note:
We're Indian-first. Most of our team is in Mumbai and Bangalore.
Our engineering culture is high-autonomy, high-accountability.
We don't have a lot of process — we expect judgment.
        """.strip()
    },
]

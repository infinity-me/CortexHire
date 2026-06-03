"""
CortexHire — Synthetic Demo Data
Realistic candidates, ranking results, and interview sessions for demo purposes.
"""
from __future__ import annotations
import json

# ─── 8 Synthetic Candidates ──────────────────────────────────

SYNTHETIC_CANDIDATES = [
    {
        "name": "Arjun Mehta",
        "email": "arjun.mehta@gmail.com",
        "headline": "Senior Backend Engineer | Payments & Distributed Systems",
        "location": "Bengaluru, India",
        "summary": "5 years building high-throughput payment systems at Razorpay and a Series A fintech. Strong Go and Java background. Led migration of payment processing from monolith to event-driven architecture handling 50K TPS.",
        "years_experience": 5.5,
        "education_tier": "tier1",
        "education_detail": "B.Tech Computer Science, IIT Bombay",
        "skills": ["Go", "Java", "Kafka", "PostgreSQL", "Redis", "Kubernetes", "PCI-DSS", "gRPC"],
        "career_history": [
            {"company": "Razorpay", "title": "Senior Software Engineer", "years": 2.5, "impact": "Led payments core team, reduced failure rate from 1.2% to 0.3%"},
            {"company": "PayFast (Series A)", "title": "Backend Engineer", "years": 2.0, "impact": "Built reconciliation engine processing $500M/month"},
            {"company": "Wipro", "title": "Software Engineer", "years": 1.0, "impact": "Java microservices development"},
        ],
        "capability_profile": {"technical_depth": 0.88, "ownership": 0.85, "execution_speed": 0.80, "communication": 0.72, "leadership": 0.65},
    },
    {
        "name": "Priya Sharma",
        "email": "priya.sharma@outlook.com",
        "headline": "ML Engineer | Recommendation Systems & NLP",
        "location": "Remote (Pune, India)",
        "summary": "4 years in ML engineering with focus on recommendation systems at a major e-commerce platform. Published 2 papers on collaborative filtering. Built and shipped PyTorch-based recommender reducing churn by 18%.",
        "years_experience": 4.0,
        "education_tier": "tier1",
        "education_detail": "M.Tech AI/ML, IIT Delhi",
        "skills": ["Python", "PyTorch", "TensorFlow", "Spark", "Airflow", "A/B Testing", "Collaborative Filtering", "Feature Stores"],
        "career_history": [
            {"company": "Flipkart", "title": "ML Engineer II", "years": 2.5, "impact": "Built real-time product recommendation engine, 23% CTR improvement"},
            {"company": "Swiggy", "title": "Data Scientist", "years": 1.5, "impact": "Restaurant recommendation model, A/B framework design"},
        ],
        "capability_profile": {"technical_depth": 0.85, "research_ability": 0.90, "production_ml": 0.80, "communication": 0.78, "ownership": 0.70},
    },
    {
        "name": "Rohan Desai",
        "email": "rohan.desai@protonmail.com",
        "headline": "Full-Stack Engineer | Python + React | Startup Veteran",
        "location": "Remote (Mumbai, India)",
        "summary": "7 years as a full-stack generalist. Employee #4 at two startups, both acquired. Comfortable making architectural decisions solo. Climate-tech adjacent — built ESG reporting dashboard for a supply chain company.",
        "years_experience": 7.0,
        "education_tier": "tier2",
        "education_detail": "B.E. Information Technology, BITS Pilani",
        "skills": ["Python", "React", "FastAPI", "PostgreSQL", "TypeScript", "Docker", "AWS", "GraphQL"],
        "career_history": [
            {"company": "SupplyTrace (Acq. by SAP)", "title": "Lead Engineer", "years": 3.0, "impact": "Built ESG data pipeline from 0, helped close $12M Series A"},
            {"company": "KiranaKart (Acq. by Zepto)", "title": "Full-Stack Engineer", "years": 2.5, "impact": "First engineering hire, built inventory management system"},
            {"company": "TCS", "title": "Software Developer", "years": 1.5, "impact": "Enterprise Java development"},
        ],
        "capability_profile": {"full_stack_breadth": 0.88, "startup_instinct": 0.92, "ownership": 0.88, "technical_depth": 0.72, "ambiguity_tolerance": 0.90},
    },
    {
        "name": "Kavya Nair",
        "email": "kavya.nair@gmail.com",
        "headline": "Platform Engineer | Kubernetes, Terraform, DevEx",
        "location": "Hyderabad, India",
        "summary": "6 years in DevOps and Platform Engineering. Reduced deploy times from 45 min to 8 min at a 800-person SaaS company. Built internal developer platform used by 600 engineers daily.",
        "years_experience": 6.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech ECE, NIT Warangal",
        "skills": ["Kubernetes", "Terraform", "GitHub Actions", "Helm", "Backstage", "ArgoCD", "Python", "Go"],
        "career_history": [
            {"company": "Chargebee", "title": "Staff Platform Engineer", "years": 3.0, "impact": "Designed IDP platform, reduced onboarding from 4 days to 4 hours"},
            {"company": "Freshworks", "title": "Senior DevOps Engineer", "years": 2.0, "impact": "Migrated 200 services to K8s, CI/CD overhaul"},
            {"company": "Infosys", "title": "DevOps Engineer", "years": 1.0, "impact": "Jenkins pipelines and infrastructure automation"},
        ],
        "capability_profile": {"platform_engineering": 0.90, "kubernetes_expertise": 0.88, "developer_empathy": 0.85, "influence": 0.72, "technical_depth": 0.80},
    },
    {
        "name": "Vikram Anand",
        "email": "vikram.anand@yahoo.com",
        "headline": "Engineering Manager | Growth Engineering | Consumer Products",
        "location": "Mumbai, India",
        "summary": "9 years in engineering, last 3 as EM. Led growth engineering team of 7 at a Series C consumer fintech, shipped referral program that drove 40% of new user acquisition.",
        "years_experience": 9.0,
        "education_tier": "tier1",
        "education_detail": "B.Tech CS, IIT Madras + MBA, IIM Ahmedabad",
        "skills": ["Team Leadership", "Growth Engineering", "A/B Testing", "Python", "React Native", "SQL", "Experimentation Platforms"],
        "career_history": [
            {"company": "BharatPe", "title": "Engineering Manager - Growth", "years": 3.0, "impact": "Led 7 engineers, referral program drove 40% new user growth"},
            {"company": "PhonePe", "title": "Senior Engineer → EM", "years": 3.5, "impact": "First growth team, shipped viral loops for UPI adoption"},
            {"company": "Amazon", "title": "Software Engineer", "years": 2.5, "impact": "Recommendation systems for India marketplace"},
        ],
        "capability_profile": {"leadership": 0.88, "growth_mindset": 0.90, "data_intuition": 0.85, "technical_depth": 0.72, "hiring_ability": 0.80},
    },
    {
        "name": "Sneha Kulkarni",
        "email": "sneha.kulkarni@gmail.com",
        "headline": "Backend Engineer | Java, Spring Boot | E-commerce",
        "location": "Pune, India",
        "summary": "3 years backend experience primarily in Java/Spring Boot for e-commerce. Good fundamentals but limited distributed systems exposure. Looking to move into fintech.",
        "years_experience": 3.0,
        "education_tier": "tier2",
        "education_detail": "B.E. CS, Pune University",
        "skills": ["Java", "Spring Boot", "MySQL", "REST APIs", "Docker", "Git"],
        "career_history": [
            {"company": "Myntra", "title": "Software Engineer", "years": 2.0, "impact": "Order management backend services"},
            {"company": "Accenture", "title": "Associate Software Engineer", "years": 1.0, "impact": "Java microservices for retail client"},
        ],
        "capability_profile": {"technical_depth": 0.60, "ownership": 0.62, "execution_speed": 0.65, "communication": 0.70, "growth_potential": 0.80},
    },
    {
        "name": "Aarav Singh",
        "email": "aarav.singh@gmail.com",
        "headline": "Data Scientist | ML | NLP | Python",
        "location": "Delhi, India",
        "summary": "2.5 years in data science, primarily notebooks and dashboards. Limited production ML experience. Strong in Python and statistical analysis but hasn't owned end-to-end ML deployment.",
        "years_experience": 2.5,
        "education_tier": "tier1",
        "education_detail": "M.Sc. Statistics, Delhi School of Economics",
        "skills": ["Python", "Pandas", "Scikit-learn", "SQL", "Tableau", "NLP basics"],
        "career_history": [
            {"company": "Deloitte Analytics", "title": "Data Scientist", "years": 1.5, "impact": "Churn prediction models for telecom client (Jupyter notebooks)"},
            {"company": "Internship - Ola", "title": "Data Science Intern", "years": 1.0, "impact": "Demand forecasting analysis"},
        ],
        "capability_profile": {"statistical_knowledge": 0.80, "production_ml": 0.35, "ownership": 0.50, "communication": 0.68, "research_ability": 0.72},
    },
    {
        "name": "Deepa Krishnan",
        "email": "deepa.krishnan@gmail.com",
        "headline": "Senior Platform Engineer | Cloud Infrastructure | AWS",
        "location": "Bengaluru, India",
        "summary": "8 years in cloud infrastructure and platform engineering. Expert in AWS and GCP. Built multi-tenant Kubernetes clusters. Strong background but prefers infrastructure over developer experience tooling.",
        "years_experience": 8.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech IT, VIT University",
        "skills": ["AWS", "GCP", "Terraform", "Kubernetes", "Prometheus", "Grafana", "Python", "Bash"],
        "career_history": [
            {"company": "Atlassian", "title": "Senior Infrastructure Engineer", "years": 3.5, "impact": "Multi-region K8s clusters, 99.99% uptime SLA"},
            {"company": "MuSigma", "title": "Cloud Engineer", "years": 2.5, "impact": "AWS infrastructure for 50+ clients"},
            {"company": "HCL", "title": "Systems Engineer", "years": 2.0, "impact": "Linux administration and automation"},
        ],
        "capability_profile": {"cloud_expertise": 0.92, "kubernetes_expertise": 0.85, "developer_empathy": 0.55, "influence": 0.60, "platform_engineering": 0.78},
    },
]


# ─── Ranking Run Data (for ZetaPay job — index 0) ────────────
# Candidates ranked by fit for "Senior Backend Engineer — Payments"

RANKING_RESULTS = [
    # (candidate_index, rank, fit_score, risk_score, growth_score, confidence_score, success_prob, shortlisted, explanation)
    (0, 1, 91.5, 15.0, 85.0, 88.0, 87.5, True,
     "Arjun is an exceptional fit. Direct payments experience at Razorpay, demonstrated ownership (reduced failure rate from 1.2% to 0.3%), and strong Go/Kafka/PostgreSQL stack match exactly what ZetaPay needs. Low risk — proven performer in identical context."),
    (3, 2, 78.0, 22.0, 82.0, 80.0, 75.0, True,
     "Kavya brings strong distributed systems thinking and infrastructure ownership. Slightly tangential — platform engineering vs payments engineering — but the problem-solving mindset and technical depth are highly transferable. Worth a conversation."),
    (2, 3, 72.5, 30.0, 78.0, 70.0, 68.0, True,
     "Rohan's startup velocity and full-stack ownership are genuine strengths. The fintech exposure through SupplyTrace is a plus. Risk: hasn't worked at the transaction volume ZetaPay operates. Would need hands-on payments ramp-up."),
    (5, 4, 52.0, 45.0, 70.0, 55.0, 48.0, False,
     "Sneha has solid Java fundamentals which are relevant. However, 3 years experience and limited distributed systems exposure is a real gap for a 'Senior' payments role handling $2B+ volume. Strong growth potential — better fit for a mid-level role."),
    (6, 5, 38.0, 60.0, 65.0, 40.0, 32.0, False,
     "Aarav's data science background doesn't map well to payments infrastructure engineering. Statistical skills are a weak proxy for the systems engineering required here. Not recommended for this role."),
]


# ─── Interview Sessions ──────────────────────────────────────
# 7 complete sessions across different candidates and jobs

INTERVIEW_SESSIONS = [
    {
        "candidate_name": "Arjun Mehta",
        "candidate_email": "arjun.mehta@gmail.com",
        "job_index": 0,  # ZetaPay — Payments Engineer
        "status": "complete",
        "total_score": 84.2,
        "answer_quality_score": 88.0,
        "communication_score": 82.0,
        "posture_score": 78.0,
        "engagement_score": 85.0,
        "confidence_score": 88.0,
        "questions": [
            "Walk me through the most complex distributed systems problem you've solved in a payments context.",
            "How would you design a payment failure detection and recovery system for 50K TPS?",
            "Tell me about a production incident you owned from detection to post-mortem.",
            "What does 'owning outcomes' mean to you — give me a specific example from your career.",
            "How do you approach PCI-DSS compliance in an evolving microservices architecture?",
            "If you joined ZetaPay tomorrow, what would you do in your first 30 days?"
        ],
        "answers": [
            {
                "q": "Walk me through the most complex distributed systems problem you've solved in a payments context.",
                "transcript": "At Razorpay, we had a distributed transaction problem where our idempotency layer was failing under network partitions. We were losing about 0.4% of payment acknowledgments — not failed payments, but acknowledgments — which meant merchants were getting confused statuses. I led the redesign of our idempotency key storage using a two-phase commit pattern across Redis and Postgres with saga orchestration for rollback. Took 3 months end-to-end, reduced ambiguous states by 94%.",
                "answer_quality": 92.0, "communication": 85.0, "posture": 80.0, "engagement": 88.0, "confidence": 90.0,
                "feedback": {"strength": "Extremely specific — named the exact problem (idempotency under network partition), the approach (2PC + saga), and quantified the result (94% reduction). This is how strong engineers talk.", "weakness": "Didn't mention team size or whether he led or was a key contributor — slightly unclear on personal ownership vs team effort.", "overall_comment": "Strong technical answer with real depth. Demonstrates distributed systems expertise directly applicable to ZetaPay's challenges."}
            },
            {
                "q": "How would you design a payment failure detection and recovery system for 50K TPS?",
                "transcript": "I'd design this in three layers. First, a real-time anomaly detector using a sliding window counter per payment gateway with configurable thresholds — if failure rate crosses 0.5% in 60 seconds, trigger alert. Second, a circuit breaker pattern for each gateway with automatic fallback routing. Third, a recovery queue that retries failed payments with exponential backoff and dead-letter handling. For 50K TPS, the detection layer needs to be in Redis with sub-millisecond reads. I'd also add a separate reconciliation job that runs every 5 minutes to catch anything the real-time layer misses.",
                "answer_quality": 90.0, "communication": 88.0, "posture": 78.0, "engagement": 85.0, "confidence": 92.0,
                "feedback": {"strength": "Structured three-layer design shows systems thinking. Mentioned specific tools (Redis), specific thresholds, and included the reconciliation safety net — shows production experience.", "weakness": "Didn't address the monitoring/observability layer or how you'd test this at load.", "overall_comment": "Excellent design answer — immediately actionable, no hand-waving. Would hire based on this answer alone."}
            },
            {
                "q": "Tell me about a production incident you owned from detection to post-mortem.",
                "transcript": "In March last year we had a cascade failure. A Redis cluster went down during peak hours, which took out our idempotency check, which caused duplicate payment processing, which then triggered our fraud system, which started blocking legit transactions. I was paged at 2 AM. My first call was to confirm blast radius — we had 12 minutes of duplicate charges totaling about 80 lakhs. I immediately rolled back to backup reconciliation, fixed the Redis cluster, then coordinated with the finance team on refunds. Post-mortem identified that we had no fallback for Redis failure — we added a local cache layer as a result.",
                "answer_quality": 91.0, "communication": 86.0, "posture": 75.0, "engagement": 82.0, "confidence": 88.0,
                "feedback": {"strength": "Told a real, high-stakes story with actual numbers (80 lakhs, 12 minutes, 2 AM page). The cascade failure explanation shows deep understanding of system interdependencies.", "weakness": "Could have elaborated on what the post-mortem process looked like and who was involved.", "overall_comment": "This answer separates engineers who've been in the fire from those who haven't. Strong."}
            },
            {
                "q": "What does 'owning outcomes' mean to you — give me a specific example.",
                "transcript": "To me it means you don't stop when your code is deployed — you stop when the problem is solved. At PayFast I shipped a reconciliation engine that was technically correct but the ops team was complaining it was slow to investigate discrepancies. That wasn't in my original spec. But I spent an extra two weeks building an investigation dashboard for them. That reduced their resolution time from 2 hours to 15 minutes. Nobody asked me to do that.",
                "answer_quality": 88.0, "communication": 84.0, "posture": 78.0, "engagement": 88.0, "confidence": 86.0,
                "feedback": {"strength": "Excellent example — went beyond spec to solve the real problem, not just the stated problem. '15 minutes vs 2 hours' is a compelling metric.", "weakness": "Slightly short — could have said more about the decision to go beyond scope and any pushback he navigated.", "overall_comment": "Authentic answer that reveals genuine ownership mindset rather than a rehearsed response."}
            },
            {
                "q": "How do you approach PCI-DSS compliance in an evolving microservices architecture?",
                "transcript": "PCI-DSS in a microservices world is about minimizing the cardholder data environment — the CDE. The principle is: don't store what you don't need, and for what you do store, isolate it. We used tokenization at the edge so card data never touched our main services. The CDE was exactly 3 services: tokenizer, vault, and charge processor. Everything else was out of scope. For audits we had separate network segmentation, access logs, and quarterly penetration tests. The challenge is when teams accidentally expand the CDE — we had a policy that any new service touching payment data needed a security review first.",
                "answer_quality": 85.0, "communication": 80.0, "posture": 76.0, "engagement": 80.0, "confidence": 84.0,
                "feedback": {"strength": "Smart answer — immediately jumped to 'minimize the CDE' which is the right mental model. Tokenization approach shows practical compliance experience.", "weakness": "Didn't mention SAQ types or how you handle third-party integrations in the compliance boundary.", "overall_comment": "Solid compliance knowledge that's clearly earned through practice, not just studied."}
            },
            {
                "q": "If you joined ZetaPay tomorrow, what would you do in your first 30 days?",
                "transcript": "First week: shadow every on-call rotation, read every post-mortem from the last 6 months, and meet every engineer one-on-one. I want to understand where the bodies are buried before I touch anything. Second and third week: trace one payment end-to-end through the system, draw the architecture diagram myself, identify the three riskiest single points of failure. Fourth week: write up my findings, propose a 90-day roadmap, and validate it with the CTO. I wouldn't ship a single line of code in the first 30 days unless there was a critical bug.",
                "answer_quality": 87.0, "communication": 88.0, "posture": 80.0, "engagement": 90.0, "confidence": 90.0,
                "feedback": {"strength": "Exceptional maturity — 'I wouldn't ship a single line of code in 30 days unless critical bug' shows senior judgment. The plan is specific and practical.", "weakness": "None significant. Minor: could mention how he'd build relationships with product/business stakeholders.", "overall_comment": "This answer would make most hiring managers want to say yes immediately."}
            },
        ]
    },
    {
        "candidate_name": "Priya Sharma",
        "candidate_email": "priya.sharma@outlook.com",
        "job_index": 1,  # StreamNova — ML Engineer
        "status": "complete",
        "total_score": 78.6,
        "answer_quality_score": 82.0,
        "communication_score": 76.0,
        "posture_score": 74.0,
        "engagement_score": 80.0,
        "confidence_score": 78.0,
        "questions": [
            "Describe your most impactful production recommendation system — what was the business impact?",
            "How would you approach reducing 42% monthly churn through personalization?",
            "Walk me through how you design and run an A/B test for a recommendation algorithm.",
            "What's the difference between offline and online evaluation for recommenders? How do you use both?",
            "Tell me about a model that failed in production. What happened and what did you learn?",
        ],
        "answers": [
            {"q": "Describe your most impactful production recommendation system — what was the business impact?", "transcript": "At Flipkart I built the real-time product recommendation engine for the homepage carousel. It was a two-tower neural network trained on user interaction sequences, served via feature store with p99 latency under 50ms. We ran a 6-week A/B test and saw 23% uplift in click-through rate and about 8% improvement in add-to-cart. The system served 100M daily requests at peak. What made it successful was tight collaboration with the data engineering team to get the right features in real-time.", "answer_quality": 88.0, "communication": 80.0, "posture": 75.0, "engagement": 82.0, "confidence": 80.0, "feedback": {"strength": "Specific architecture (two-tower neural net), specific metrics (23% CTR, 50ms p99, 100M requests), and mentioned cross-functional collaboration.", "weakness": "Didn't explain the iteration process — how many versions before this worked?", "overall_comment": "Solid answer demonstrating production ML experience at meaningful scale."}},
            {"q": "How would you approach reducing 42% monthly churn through personalization?", "transcript": "First I'd do a churn cohort analysis to understand why users leave — is it content exhaustion, bad cold start, wrong genre discovery? Then I'd instrument listening sessions more granularly. The 42% churn tells me the current cosine similarity approach isn't capturing taste well. I'd start with a session-based recommender that incorporates skip signals and repeat plays, not just clicks. Then layer in collaborative filtering from similar user clusters. I'd target the 'day 3 to day 7' window first — that's typically when users decide whether a new app is for them.", "answer_quality": 84.0, "communication": 78.0, "posture": 73.0, "engagement": 80.0, "confidence": 78.0, "feedback": {"strength": "Smart prioritization of the D3-D7 window. Diagnostic-first thinking is the right approach.", "weakness": "Didn't quantify what success looks like or timeline to ship first iteration.", "overall_comment": "Good strategic thinking. Shows she understands the business problem, not just the ML problem."}},
            {"q": "Walk me through how you design and run an A/B test for a recommendation algorithm.", "transcript": "I start with power analysis to determine sample size — you need to know the minimum detectable effect you care about. For recommendation changes, I prefer user-level randomization over request-level to avoid novelty bias. Define success metrics upfront: primary is engagement rate, guardrail is retention at day 30. Run for minimum 2 weeks to capture weekly seasonality. I always check for Simpson's paradox across user segments — an algorithm can win overall but lose for new users. Post-experiment, I look at long-term effects because recommendation systems can have delayed impacts on churn.", "answer_quality": 87.0, "communication": 82.0, "posture": 72.0, "engagement": 78.0, "confidence": 80.0, "feedback": {"strength": "Mentioned power analysis, user-level randomization, Simpson's paradox, and long-term effects — this is expert-level A/B testing knowledge.", "weakness": "Didn't mention how to handle interference between test and control groups in social/network contexts.", "overall_comment": "This is exactly what StreamNova needs — rigorous experimentation thinking."}},
            {"q": "What's the difference between offline and online evaluation for recommenders?", "transcript": "Offline evaluation uses historical data — metrics like NDCG, MRR, recall at K. It's fast and cheap but can be misleading because it measures how well you predict the past, not how users will behave with new recommendations. Online evaluation is A/B testing with real users. It's the ground truth but expensive — you're potentially harming user experience during the experiment. The trap is over-relying on offline metrics. At Flipkart we had a model with 15% better offline NDCG that had neutral online impact because it was optimizing for a stale user preference distribution.", "answer_quality": 85.0, "communication": 76.0, "posture": 74.0, "engagement": 78.0, "confidence": 76.0, "feedback": {"strength": "The Flipkart example of offline/online metric mismatch is the perfect real-world illustration.", "weakness": "Could have mentioned counterfactual evaluation or interleaving as intermediate options.", "overall_comment": "Clear, practical understanding of the fundamental tension in recommender evaluation."}},
            {"q": "Tell me about a model that failed in production.", "transcript": "At Swiggy I built a restaurant recommendation model for new users — cold start problem. It was working great in testing but in production we found it was systematically recommending popular restaurants regardless of location. A user in Koramangala was getting recommendations for restaurants 8 km away. The issue was our proximity feature had a bug in the feature engineering pipeline — we were calculating straight-line distance but not accounting for traffic. Real-world delivery time was 40-60 minutes for 'nearby' recommendations. We caught it through user complaints, not monitoring — which was the real failure.", "answer_quality": 78.0, "communication": 72.0, "posture": 76.0, "engagement": 82.0, "confidence": 74.0, "feedback": {"strength": "Honest answer — admitted the real failure was monitoring, not just the model bug. Shows maturity.", "weakness": "Didn't explain what monitoring they put in place after this.", "overall_comment": "Good answer. The self-awareness about monitoring gap shows growth mindset."}},
        ]
    },
    {
        "candidate_name": "Rohan Desai",
        "candidate_email": "rohan.desai@protonmail.com",
        "job_index": 3,  # Verdant — Founding Full-Stack
        "status": "complete",
        "total_score": 81.4,
        "answer_quality_score": 84.0,
        "communication_score": 80.0,
        "posture_score": 78.0,
        "engagement_score": 82.0,
        "confidence_score": 84.0,
        "questions": [
            "Tell me about building a product from zero to first users — what was the hardest part?",
            "How do you make architectural decisions when there's no senior engineer above you?",
            "Describe working with non-technical founders. How do you translate technical constraints?",
            "What do you know about Scope 3 emissions accounting? How would you approach the data problem?",
            "Walk me through a time you had to change technical direction mid-project.",
        ],
        "answers": [
            {"q": "Tell me about building a product from zero to first users — what was the hardest part?", "transcript": "At SupplyTrace I was employee 4, first technical hire. The hardest part wasn't the code — it was deciding what NOT to build. The founders wanted 12 features for launch. I pushed back hard and said we'd launch with 2 core features or we'd never launch. The hardest conversation was telling them their 'must-have' enterprise reporting module was a month of work and we didn't need it to learn whether the product was useful. We launched 6 weeks later with import + visualization. We had 8 customers in month 1. The reporting module came 3 months later when we knew exactly what customers needed.", "answer_quality": 88.0, "communication": 84.0, "posture": 78.0, "engagement": 84.0, "confidence": 86.0, "feedback": {"strength": "Courageous scope management. The 'hardest part was what NOT to build' framing immediately signals startup maturity.", "weakness": "None significant.", "overall_comment": "Exactly the mindset a stealth startup engineer #3 needs."}},
            {"q": "How do you make architectural decisions when there's no senior engineer above you?", "transcript": "I write an RFC. Even if it's just for myself. Forces me to articulate tradeoffs. For bigger decisions I use a simple framework: what's the cost of being wrong? If the decision is easily reversible, I bias toward shipping fast. If it's not reversible — database choice, API contracts, data models — I slow down and consult externally. I've built a network of senior engineers I trust who I can get on a call with. At SupplyTrace my biggest architectural decision was choosing FastAPI over Django — I spent a week prototyping both, wrote up the tradeoffs, and got two external opinions before committing.", "answer_quality": 86.0, "communication": 82.0, "posture": 78.0, "engagement": 80.0, "confidence": 84.0, "feedback": {"strength": "RFC culture + reversibility framework + external network — this is a mature, self-aware approach to engineering leadership without formal authority.", "weakness": "Could have mentioned how he handles situations where the external opinions conflict.", "overall_comment": "Strong. Shows he's learned to compensate for lack of internal mentorship."}},
            {"q": "Describe working with non-technical founders.", "transcript": "I've worked directly with non-technical founders for 5+ years. The key is translating decisions into business outcomes, not technical explanations. Instead of 'we need to refactor the data pipeline,' it's 'right now every new customer type costs us 3 weeks of dev time — if we fix this, we can onboard a new industry in 3 days.' I've also learned to under-promise on timelines and over-deliver. Founders under funding pressure have a natural tendency to tell investors what they want to hear about timelines. I push back on that — I'd rather be the person who says 'that's 6 weeks' and deliver in 5 than promise 3 weeks and deliver in 7.", "answer_quality": 85.0, "communication": 84.0, "posture": 80.0, "engagement": 84.0, "confidence": 82.0, "feedback": {"strength": "The timeline management approach is wise and builds long-term trust.", "weakness": "Could mention how he handles founder pushback when they disagree with his estimates.", "overall_comment": "Demonstrates high EQ and cross-functional communication skills critical for an early-stage engineer."}},
            {"q": "What do you know about Scope 3 emissions accounting?", "transcript": "Scope 3 is indirect emissions from a company's value chain — upstream suppliers and downstream product use. It's the hardest scope because you don't control it. At SupplyTrace we were adjacent to this — we were tracking supply chain data for compliance, and several customers asked us about emissions data. The key challenge is data quality — suppliers often don't know their own emissions, so you're dealing with estimates, emission factors, and a lot of interpolation. The GHG Protocol is the standard framework. I'd approach the data problem by starting with what's measurable directly, then building a confidence layer that shows customers where their data is solid vs estimated.", "answer_quality": 80.0, "communication": 78.0, "posture": 76.0, "engagement": 80.0, "confidence": 80.0, "feedback": {"strength": "GHG Protocol knowledge is relevant. The 'confidence layer' idea for data quality transparency is sophisticated and valuable.", "weakness": "Admitted limited direct experience — honest but shows a gap for a climate-tech company.", "overall_comment": "Honest, curious answer. Shows intellectual engagement with the domain even without deep expertise."}},
            {"q": "Walk me through a time you had to change technical direction mid-project.", "transcript": "At KiranaKart we were 6 weeks into building a real-time inventory sync system using WebSockets. Mid-project I realized our mobile app couldn't maintain persistent WebSocket connections on 2G networks — which was 60% of our users. We had to pivot to a polling mechanism with smart caching. The painful part was telling the CEO we were restarting a month of work. I framed it as 'we discovered we were solving the wrong problem' rather than 'we made a mistake.' The polling solution we shipped actually had better battery life and worked more reliably. Sometimes the hard pivot is the right move.", "answer_quality": 83.0, "communication": 80.0, "posture": 78.0, "engagement": 82.0, "confidence": 82.0, "feedback": {"strength": "Good real-world example with technical nuance (2G constraint), and the framing advice ('wrong problem vs mistake') is genuinely useful.", "weakness": "Could elaborate on how he identified the issue before it became a bigger disaster.", "overall_comment": "Solid engineering judgment demonstrated through concrete example."}},
        ]
    },
    {
        "candidate_name": "Kavya Nair",
        "candidate_email": "kavya.nair@gmail.com",
        "job_index": 2,  # Mosaic — Staff Platform Engineer
        "status": "complete",
        "total_score": 86.8,
        "answer_quality_score": 90.0,
        "communication_score": 84.0,
        "posture_score": 82.0,
        "engagement_score": 86.0,
        "confidence_score": 88.0,
        "questions": [
            "Describe how you reduced deploy times from 45 minutes to under 10 minutes. What was the approach?",
            "How do you get 1200 engineers to adopt a new internal platform they didn't ask for?",
            "What does a good internal developer platform look like? What makes developers actually use it?",
            "Walk me through a platform initiative that failed. What went wrong?",
            "How do you measure success for a developer platform?",
        ],
        "answers": [
            {"q": "Describe how you reduced deploy times from 45 minutes to under 10 minutes.", "transcript": "At Chargebee the 45-minute deploys were a combination of three bottlenecks: slow Docker builds (20 min), sequential integration tests (15 min), and manual approval gates (10 min). I fixed them in parallel streams. For Docker: layer caching strategy + switching to BuildKit reduced builds to 4 minutes. For tests: parallelized test suites across 8 runners, went from 15 to 4 minutes. For approvals: implemented automated deployment to staging with auto-approval if all checks pass, manual gate only for production. Total: 8 minutes average deploy time. More importantly, we went from 3 deploys per day to 18 per day.", "answer_quality": 93.0, "communication": 86.0, "posture": 82.0, "engagement": 88.0, "confidence": 90.0, "feedback": {"strength": "Perfect answer. Named the three bottlenecks, named the interventions, quantified both time and business impact (3→18 deploys/day). Shows deep technical knowledge plus business thinking.", "weakness": "None.", "overall_comment": "This is the exact answer Mosaic is hiring for. Hire."}},
            {"q": "How do you get 1200 engineers to adopt a new internal platform?", "transcript": "You don't force adoption — you make the right path the easy path. My approach at Chargebee was to identify 5 'power users' from high-influence teams early. Work with them intensively, make their lives noticeably better, then let them evangelize. Engineers trust other engineers more than platform team documentation. Second: golden paths have to be genuinely better, not just 'the official way.' If using the platform takes 30 extra minutes, you've failed before you started. Third: I ran 'office hours' every Tuesday — any engineer could bring their deployment problem. Fixed their pain live, in public, in Slack. That became our best marketing.", "answer_quality": 91.0, "communication": 88.0, "posture": 84.0, "engagement": 88.0, "confidence": 88.0, "feedback": {"strength": "Power users + golden paths + office hours — this is sophisticated internal product management thinking wrapped in engineering language.", "weakness": "Didn't mention measuring adoption rates or handling resistant teams.", "overall_comment": "This is exactly what Mosaic said the previous person failed at. This candidate can do it."}},
            {"q": "What does a good internal developer platform look like?", "transcript": "A good IDP is invisible when it's working and immediately obvious when it's not. Concretely: onboard a new service in under an hour from scratch. Deploy to staging in under 5 minutes. Get your service into production with appropriate runbooks, alerting, and logging pre-configured. Every team shouldn't have to solve the same problems. The worst IDPs I've seen fail because they optimize for the platform team's architecture principles rather than developer speed. A developer shouldn't need to read 40 pages of docs to ship a feature.", "answer_quality": 88.0, "communication": 84.0, "posture": 80.0, "engagement": 85.0, "confidence": 86.0, "feedback": {"strength": "'Invisible when working' is the right mental model. Concrete metrics (onboard in <1 hour, deploy in <5 min) show operational experience.", "weakness": "Could have mentioned specific tools like Backstage or how you handle multi-language service diversity.", "overall_comment": "Strong platform philosophy backed by real-world constraints."}},
            {"q": "Walk me through a platform initiative that failed.", "transcript": "I built a service mesh at Freshworks — Istio-based, beautiful architecture, full observability. Took 6 months. Three teams adopted it in the first quarter. Then adoption stalled. The problem: I'd built something technically excellent but hadn't worked with any product teams during design. The mTLS requirement broke their test environments in ways they weren't equipped to debug. I learned too late that I'd optimized for security compliance requirements, not for developer experience. We ended up building a 'light mode' that bypassed mTLS for non-production. 2 months wasted, team trust damaged. Biggest lesson: involve engineers from 3-4 teams from week 1, not week 25.", "answer_quality": 89.0, "communication": 82.0, "posture": 81.0, "engagement": 84.0, "confidence": 84.0, "feedback": {"strength": "Very honest and specific failure story with clear lesson extracted. Shows she can learn from mistakes and communicate transparently.", "weakness": "None — this is exactly the kind of failure story you want to hear.", "overall_comment": "The lesson learned directly addresses Mosaic's stated problem (last person failed due to adoption issues)."}},
            {"q": "How do you measure success for a developer platform?", "transcript": "Three tiers of metrics. Tier 1: deployment frequency and lead time — these are the DORA metrics, they're the most direct measure of developer velocity. Tier 2: platform adoption and NPS — what percentage of teams are using the golden paths vs rolling their own, and do they actually like it. Tier 3: toil reduction — hours per week engineers spend on deployment/infrastructure tasks vs building product features. I run quarterly surveys alongside automated metrics. The most honest measure is unsolicited adoption — when teams from outside your pilot group start using the platform because word spread.", "answer_quality": 90.0, "communication": 84.0, "posture": 82.0, "engagement": 86.0, "confidence": 88.0, "feedback": {"strength": "DORA metrics + NPS + toil reduction + unsolicited adoption is a comprehensive measurement framework. Shows she thinks in outcomes, not outputs.", "weakness": "None significant.", "overall_comment": "Excellent answer. She's thought deeply about platform engineering as a product discipline."}},
        ]
    },
    {
        "candidate_name": "Vikram Anand",
        "candidate_email": "vikram.anand@yahoo.com",
        "job_index": 4,  # Khata — Engineering Manager Growth
        "status": "complete",
        "total_score": 79.5,
        "answer_quality_score": 83.0,
        "communication_score": 82.0,
        "posture_score": 72.0,
        "engagement_score": 78.0,
        "confidence_score": 80.0,
        "questions": [
            "Tell me about a growth initiative you led that measurably moved retention or activation.",
            "How do you manage engineers who are stronger technically than you?",
            "Describe your approach to building an experimentation platform from scratch.",
            "What does good look like for a growth engineering team at Khata's scale?",
            "Tell me about a time you had to let someone go.",
        ],
        "answers": [
            {"q": "Tell me about a growth initiative you led that measurably moved retention or activation.", "transcript": "At BharatPe I led the referral program from conception to 40% of new user acquisition. The insight was that merchants trust other merchants — digital marketing was expensive and impersonal. We built a peer referral system with instant Paytm cashback for referrers and an accelerated onboarding flow for referred merchants. The activation rate for referred users was 68% vs 34% for organic. I managed a team of 4 engineers and 2 data scientists for this. We shipped in 8 weeks, which was fast for BharatPe at the time.", "answer_quality": 88.0, "communication": 85.0, "posture": 74.0, "engagement": 80.0, "confidence": 82.0, "feedback": {"strength": "68% vs 34% activation is a compelling metric. Clear ownership of the full initiative.", "weakness": "Didn't mention what metrics were measured during development to know if they were on track.", "overall_comment": "Strong growth engineering leadership example with real business impact."}},
            {"q": "How do you manage engineers who are stronger technically than you?", "transcript": "I've always had engineers on my team who are better at writing code than me — that's how it should be. My job is to remove their blockers, not to be their most technical person. What I add is context, prioritization, and protection from organizational noise. I've found the best approach is radical transparency about decisions — I explain why we're building X before Y, not just what to build. Strong engineers hate arbitrary direction. They'll execute well if they understand the reasoning and feel heard when they disagree.", "answer_quality": 82.0, "communication": 84.0, "posture": 72.0, "engagement": 78.0, "confidence": 80.0, "feedback": {"strength": "Mature and honest perspective on engineering management. 'Protection from organizational noise' is a real EM value-add.", "weakness": "A bit abstract — a concrete story of managing a technically stronger engineer would strengthen this.", "overall_comment": "Good management philosophy but needs more specific examples."}},
            {"q": "Describe your approach to building an experimentation platform from scratch.", "transcript": "An experimentation platform has three core components: experiment assignment (who sees what), tracking (what happened), and analysis (did it work). Start with experiment assignment — user-level bucketing with consistent hashing so users don't flip between variants. Use your existing analytics event pipeline for tracking, don't build a separate one. For analysis, start with the simplest correct thing: a Bayesian framework with a shared Jupyter template. What I've seen fail is building the perfect platform before anyone uses it. Khata's 20+ tests per month with no framework is actually an advantage — there's immediate demand. Ship a simple version in 4 weeks and iterate.", "answer_quality": 85.0, "communication": 82.0, "posture": 72.0, "engagement": 78.0, "confidence": 80.0, "feedback": {"strength": "Practical, ship-first mindset. Correctly identified starting with assignment + existing analytics pipeline.", "weakness": "Didn't address mutual exclusivity, traffic allocation, or guardrail metrics — important for mature experimentation.", "overall_comment": "Good directional answer. Shows practical experience building rather than just designing experimentation systems."}},
            {"q": "What does good look like for a growth engineering team at Khata's scale?", "transcript": "At 3M users and 8% MoM growth, a good growth team is running 5-6 concurrent experiments at different funnel stages, has a 2-week ship cycle for most features, and directly owns and monitors their metric dashboard — not waiting for a data team report. 'Good' also means the team can distinguish between correlation and causation in their metrics. I've seen growth teams celebrate 'wins' that were seasonality effects. Good growth engineering is slow to declare victory and fast to kill things that aren't working.", "answer_quality": 84.0, "communication": 82.0, "posture": 72.0, "engagement": 76.0, "confidence": 80.0, "feedback": {"strength": "The 'slow to declare victory, fast to kill what isn't working' ethos is rare and valuable.", "weakness": "Could be more specific about team structure and how growth engineering interfaces with product teams.", "overall_comment": "Good answer showing growth engineering maturity."}},
            {"q": "Tell me about a time you had to let someone go.", "transcript": "I had an engineer who was technically strong but consistently delivered features that engineering loved and users didn't understand. UX was an afterthought. After three months of coaching — pairing him with design, asking him to conduct user interviews, specific feedback in 1:1s — the pattern didn't change. The letting-go conversation was the hardest I've had as a manager. I was direct: this team needs engineers who own the full outcome including user experience, and that's not where your strengths are. He went to a more infrastructure-focused team and thrived. I learned that performance management has to start earlier than I was comfortable with.", "answer_quality": 82.0, "communication": 80.0, "posture": 70.0, "engagement": 76.0, "confidence": 78.0, "feedback": {"strength": "Shows he can make hard people decisions and be direct. The 'started earlier' learning shows genuine reflection.", "weakness": "Could describe more specifically what the coaching looked like before the decision.", "overall_comment": "Shows the managerial courage that's rare and necessary at senior levels."}},
        ]
    },
    {
        "candidate_name": "Sneha Kulkarni",
        "candidate_email": "sneha.kulkarni@gmail.com",
        "job_index": 0,  # ZetaPay — Payments Engineer
        "status": "complete",
        "total_score": 54.8,
        "answer_quality_score": 55.0,
        "communication_score": 60.0,
        "posture_score": 52.0,
        "engagement_score": 56.0,
        "confidence_score": 50.0,
        "questions": [
            "Walk me through the most technically complex backend system you've built.",
            "How do you design for high availability in a payments system?",
            "Tell me about a time you had to debug a production issue under pressure.",
            "What do you know about distributed transactions?",
        ],
        "answers": [
            {"q": "Walk me through the most technically complex backend system you've built.", "transcript": "At Myntra I built the order management system. It handled the full order lifecycle from placement to delivery tracking. We used Spring Boot for the backend, MySQL for the database, and Redis for caching. The system processed about 10,000 orders per day. I worked on the state machine for order status transitions and the notifications service.", "answer_quality": 55.0, "communication": 62.0, "posture": 54.0, "engagement": 58.0, "confidence": 52.0, "feedback": {"strength": "Described the system coherently and mentioned specific technologies.", "weakness": "10,000 orders/day is low scale for a 'Senior' payments role. No mention of failure handling, consistency challenges, or architectural decisions.", "overall_comment": "Solid junior-to-mid level answer. Doesn't demonstrate the depth expected for ZetaPay's senior role."}},
            {"q": "How do you design for high availability in a payments system?", "transcript": "High availability is about making sure the system doesn't go down. You use load balancers, multiple instances, and database replication. We had a primary-replica setup in MySQL. If the primary goes down, the replica takes over. We also had retry logic in the application layer for transient failures.", "answer_quality": 48.0, "communication": 58.0, "posture": 50.0, "engagement": 54.0, "confidence": 48.0, "feedback": {"strength": "Correctly identified basic HA concepts (load balancing, replication, retries).", "weakness": "Very surface-level answer. No mention of consistency guarantees, split-brain scenarios, circuit breakers, or the specific challenges of payment idempotency during failover.", "overall_comment": "Textbook answer without depth. This role requires someone who has lived through production HA failures."}},
            {"q": "Tell me about a time you had to debug a production issue under pressure.", "transcript": "We had an incident where orders were failing to process. I checked the logs and found that the database connection pool was exhausted. I increased the pool size as a quick fix and the issue resolved. Then I investigated why connections were being held and found a query that wasn't closing connections properly. I fixed the query and deployed.", "answer_quality": 58.0, "communication": 62.0, "posture": 52.0, "engagement": 56.0, "confidence": 50.0, "feedback": {"strength": "Described a real production issue with a logical diagnosis and fix.", "weakness": "The fix (increase pool size) was a bandaid, not a root cause fix. The scale seems small. No mention of customer impact, how long it took, or what she learned.", "overall_comment": "Functional incident response but lacks the urgency and depth expected in a payments context."}},
            {"q": "What do you know about distributed transactions?", "transcript": "Distributed transactions are transactions that span multiple databases or services. You can use two-phase commit to ensure all services either commit or rollback together. There's also the saga pattern which is an alternative. I haven't personally implemented these but I've read about them.", "answer_quality": 45.0, "communication": 58.0, "posture": 50.0, "engagement": 54.0, "confidence": 48.0, "feedback": {"strength": "Correctly named the key patterns (2PC, saga).", "weakness": "Admitted no hands-on experience. For a payments engineering role at this level, theoretical knowledge is insufficient.", "overall_comment": "Honest admission of lack of experience, which is respectable, but this is a must-have skill for the role."}},
        ]
    },
    {
        "candidate_name": "Aarav Singh",
        "candidate_email": "aarav.singh@gmail.com",
        "job_index": 1,  # StreamNova — ML Engineer
        "status": "complete",
        "total_score": 47.2,
        "answer_quality_score": 46.0,
        "communication_score": 52.0,
        "posture_score": 48.0,
        "engagement_score": 50.0,
        "confidence_score": 44.0,
        "questions": [
            "Describe a recommendation system you've built and deployed to production.",
            "How would you design an A/B test for a new recommendation algorithm?",
            "What experience do you have with PyTorch or TensorFlow in production?",
            "How do you approach reducing user churn using ML?",
        ],
        "answers": [
            {"q": "Describe a recommendation system you've built and deployed to production.", "transcript": "I built a recommendation model for a telecom client at Deloitte. It was a churn prediction model using logistic regression and random forests. The model was about 82% accurate. I used Python and scikit-learn. It was deployed as a batch job that ran weekly and generated a list of at-risk customers for the retention team to contact.", "answer_quality": 42.0, "communication": 52.0, "posture": 48.0, "engagement": 48.0, "confidence": 44.0, "feedback": {"strength": "Mentioned specific accuracy metric and deployment model.", "weakness": "This is a churn prediction model, not a recommendation system. Fundamentally different problem. Doesn't address real-time serving, user-item relevance, or the actual recommendation engineering required.", "overall_comment": "Answered a different question than was asked. Suggests limited experience with actual recommendation systems."}},
            {"q": "How would you design an A/B test for a new recommendation algorithm?", "transcript": "I would split the users into two groups, one seeing the old recommendations and one seeing the new ones. Then measure the click-through rate after two weeks and see which one is higher. Use a t-test to check if the difference is statistically significant.", "answer_quality": 40.0, "communication": 50.0, "posture": 46.0, "engagement": 48.0, "confidence": 40.0, "feedback": {"strength": "Basic correct understanding of A/B test structure.", "weakness": "No mention of sample size calculation, user-level vs request-level randomization, novelty effects, or guardrail metrics. t-test is too simple for this context.", "overall_comment": "Junior-level A/B testing knowledge. Insufficient for an ML Engineer role at StreamNova."}},
            {"q": "What experience do you have with PyTorch or TensorFlow in production?", "transcript": "I've used scikit-learn extensively and have some experience with TensorFlow from online courses. I've done the deep learning specialization on Coursera. I haven't deployed neural network models to production but I'm a fast learner and I'm confident I can pick it up quickly.", "answer_quality": 35.0, "communication": 52.0, "posture": 48.0, "engagement": 50.0, "confidence": 40.0, "feedback": {"strength": "Honest about experience gap.", "weakness": "This role explicitly requires production ML experience. 'Fast learner' and Coursera courses are not sufficient substitutes for actual production deployment experience in a company that needs to reduce churn now.", "overall_comment": "Honest but insufficient. StreamNova cannot afford to train someone on production ML from scratch."}},
            {"q": "How do you approach reducing user churn using ML?", "transcript": "I would look at the data to find patterns in when users churn. Build a model to predict which users are likely to churn. Then target those users with retention campaigns. We did something similar at Deloitte for the telecom client — identified high-risk users and the retention team called them.", "answer_quality": 45.0, "communication": 52.0, "posture": 50.0, "engagement": 52.0, "confidence": 46.0, "feedback": {"strength": "Understands the basic predict-then-intervene framework.", "weakness": "This describes churn prediction, not churn reduction through personalization — which is what StreamNova actually needs. The distinction matters enormously. The role is about making the product better through recommendations, not just identifying who to call.", "overall_comment": "Misses the core challenge. StreamNova needs someone who can reduce churn by improving the product, not by having a sales team call users."}},
        ]
    },
]

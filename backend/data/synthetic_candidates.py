"""
CortexHire — Synthetic Candidate Profiles
20 richly detailed candidates spanning diverse backgrounds, including:
- FAANG veterans, startup builders, open-source contributors
- Tier-1 / Tier-3 / bootcamp / self-taught backgrounds
- Career changers, candidates with gaps, international candidates
- Hidden gems designed to showcase bias correction

These profiles are deliberately crafted to stress-test ALL 10 innovations.
"""
from __future__ import annotations

SYNTHETIC_CANDIDATES: list[dict] = [
    {
        "name": "Arjun Sharma",
        "email": "arjun.sharma@example.com",
        "headline": "Senior Backend Engineer | Ex-Google | Distributed Systems",
        "location": "Bangalore, India",
        "summary": (
            "7 years building large-scale distributed systems at Google and Flipkart. "
            "Led the redesign of Google Pay's transaction pipeline handling 50M req/day. "
            "Deep expertise in Go, Kubernetes, Spanner. Strong opinions about reliability engineering."
        ),
        "years_experience": 7.0,
        "education_tier": "tier1",
        "education_detail": "B.Tech Computer Science, IIT Bombay (2017)",
        "career_history": [
            {
                "company": "Google",
                "industry": "Big Tech",
                "company_size": "100k+",
                "company_type": "enterprise",
                "title": "Senior Software Engineer",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 12,
                "impact_score": 0.92,
                "description": "Led Go-based transaction pipeline redesign. 50M req/day, 99.99% uptime."
            },
            {
                "company": "Flipkart",
                "industry": "E-commerce",
                "company_size": "10k+",
                "company_type": "enterprise",
                "title": "Software Engineer II",
                "start_year": 2018,
                "end_year": 2021,
                "team_size": 8,
                "impact_score": 0.78,
                "description": "Built inventory management microservices. Reduced latency by 40%."
            },
            {
                "company": "Google",
                "industry": "Big Tech",
                "company_type": "enterprise",
                "title": "Software Engineer (Intern)",
                "start_year": 2017,
                "end_year": 2017,
                "team_size": 0,
                "impact_score": 0.7,
                "description": "Internship on Google Cloud Spanner team."
            }
        ],
        "skills": [
            {"name": "Go", "proficiency": 0.95},
            {"name": "Kubernetes", "proficiency": 0.9},
            {"name": "Distributed Systems", "proficiency": 0.92},
            {"name": "Google Spanner", "proficiency": 0.85},
            {"name": "gRPC", "proficiency": 0.88},
            {"name": "PostgreSQL", "proficiency": 0.8},
        ],
        "achievements": [
            "Reduced transaction pipeline latency by 60% (Google Pay)",
            "Patent: Distributed lock-free queue algorithm",
            "Google I/O speaker 2023",
        ],
        "capability_profile": {
            "technical_depth": 0.93,
            "adaptability": 0.72,
            "leadership": 0.68,
            "execution": 0.88,
            "systems_thinking": 0.94,
            "creativity": 0.65,
            "resilience": 0.80,
            "communication": 0.70,
        }
    },
    {
        "name": "Priya Mehta",
        "email": "priya.mehta@example.com",
        "headline": "Full-Stack Engineer | Startup Builder | 3 Exits",
        "location": "Mumbai, India",
        "summary": (
            "Serial startup engineer with 3 successful exits. Built products from 0 to 1M users. "
            "Thrives in ambiguity, moves fast, owns outcomes. Most recently CTO of an edtech startup "
            "acquired by BYJU's. Tier-3 college, entirely self-made career."
        ),
        "years_experience": 9.0,
        "education_tier": "tier3",
        "education_detail": "B.E. Computer Science, RAIT Mumbai (2015)",
        "career_history": [
            {
                "company": "LearnFast (Acquired by BYJU's)",
                "industry": "Edtech",
                "company_size": "<50",
                "company_type": "startup",
                "title": "CTO & Co-Founder",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 15,
                "impact_score": 0.97,
                "description": "Built adaptive learning platform from scratch. 0→800K users in 18 months. Acquired."
            },
            {
                "company": "HealthZen",
                "industry": "HealthTech",
                "company_size": "<100",
                "company_type": "startup",
                "title": "Lead Engineer",
                "start_year": 2018,
                "end_year": 2021,
                "team_size": 6,
                "impact_score": 0.88,
                "description": "Led platform rebuild. Series A to acquisition in 24 months."
            },
            {
                "company": "PayLocal",
                "industry": "Fintech",
                "company_size": "<30",
                "company_type": "startup",
                "title": "Full-Stack Engineer",
                "start_year": 2015,
                "end_year": 2018,
                "team_size": 4,
                "impact_score": 0.80,
                "description": "Early engineer. Built payment gateway. Acquired by Paytm."
            }
        ],
        "skills": [
            {"name": "React", "proficiency": 0.90},
            {"name": "Node.js", "proficiency": 0.92},
            {"name": "Python", "proficiency": 0.85},
            {"name": "AWS", "proficiency": 0.88},
            {"name": "System Design", "proficiency": 0.87},
            {"name": "Technical Leadership", "proficiency": 0.90},
        ],
        "achievements": [
            "0→800K users in 18 months",
            "3 startup acquisitions",
            "Built & led 15-person engineering team",
        ],
        "capability_profile": {
            "technical_depth": 0.84,
            "adaptability": 0.97,
            "leadership": 0.93,
            "execution": 0.96,
            "systems_thinking": 0.85,
            "creativity": 0.90,
            "resilience": 0.95,
            "communication": 0.88,
        }
    },
    {
        "name": "Marcus Johnson",
        "email": "marcus.j@example.com",
        "headline": "Open Source Contributor | Self-Taught | Infrastructure Engineer",
        "location": "Lagos, Nigeria",
        "summary": (
            "Self-taught engineer, no formal CS degree. Core contributor to Prometheus and Grafana. "
            "Maintains 3 open-source tools with 12K+ GitHub stars combined. "
            "Built and runs infrastructure for a fintech serving West Africa. "
            "Fastest learner I've ever seen — ML Engineer at company who hired him."
        ),
        "years_experience": 5.0,
        "education_tier": "self-taught",
        "education_detail": "No CS degree — Economics degree, University of Lagos (2018)",
        "career_history": [
            {
                "company": "PiggyVest",
                "industry": "Fintech",
                "company_size": "200",
                "company_type": "startup",
                "title": "Infrastructure Engineer",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 3,
                "impact_score": 0.91,
                "description": "Sole infra engineer. Built observability stack. Reduced MTTR from 4h to 15min."
            },
            {
                "company": "Freelance / Open Source",
                "industry": "Open Source",
                "company_size": "1",
                "company_type": "freelance",
                "title": "Independent Engineer",
                "start_year": 2019,
                "end_year": 2021,
                "team_size": 0,
                "impact_score": 0.85,
                "description": "Prometheus contributor, built LogSpy (8K stars), MeshGuard (4K stars)."
            }
        ],
        "skills": [
            {"name": "Prometheus", "proficiency": 0.95},
            {"name": "Grafana", "proficiency": 0.92},
            {"name": "Kubernetes", "proficiency": 0.88},
            {"name": "Go", "proficiency": 0.82},
            {"name": "Linux", "proficiency": 0.93},
            {"name": "Python", "proficiency": 0.80},
        ],
        "achievements": [
            "12K+ GitHub stars across maintained OSS tools",
            "Prometheus core contributor since 2020",
            "Reduced system MTTR from 4 hours to 15 minutes",
        ],
        "capability_profile": {
            "technical_depth": 0.89,
            "adaptability": 0.94,
            "leadership": 0.70,
            "execution": 0.91,
            "systems_thinking": 0.92,
            "creativity": 0.88,
            "resilience": 0.96,
            "communication": 0.75,
        }
    },
    {
        "name": "Sarah Chen",
        "email": "sarah.chen@example.com",
        "headline": "Staff ML Engineer | Pinterest → Scale AI | Computer Vision",
        "location": "San Francisco, CA",
        "summary": (
            "Staff ML engineer specializing in computer vision and recommendation systems. "
            "Led Pinterest's visual search model used by 450M users. "
            "Built Scale AI's data pipeline for autonomous vehicle training. "
            "Ph.D. dropout — left after 2 years to go build real products."
        ),
        "years_experience": 8.0,
        "education_tier": "tier1",
        "education_detail": "M.S. Computer Science (ML focus), Stanford (2016). Ph.D. dropout 2018.",
        "career_history": [
            {
                "company": "Scale AI",
                "industry": "AI/ML",
                "company_size": "500",
                "company_type": "startup",
                "title": "Staff ML Engineer",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 8,
                "impact_score": 0.94,
                "description": "Built AV training data pipeline. 10x throughput improvement."
            },
            {
                "company": "Pinterest",
                "industry": "Social Media",
                "company_size": "3000",
                "company_type": "tech",
                "title": "Senior ML Engineer",
                "start_year": 2018,
                "end_year": 2022,
                "team_size": 6,
                "impact_score": 0.90,
                "description": "Visual search model serving 450M users. 35% engagement uplift."
            }
        ],
        "skills": [
            {"name": "PyTorch", "proficiency": 0.95},
            {"name": "Computer Vision", "proficiency": 0.94},
            {"name": "Python", "proficiency": 0.96},
            {"name": "CUDA", "proficiency": 0.88},
            {"name": "MLOps", "proficiency": 0.85},
            {"name": "Recommendation Systems", "proficiency": 0.87},
        ],
        "achievements": [
            "Visual search model used by 450M Pinterest users",
            "10x AV training data throughput at Scale AI",
            "5 papers at NeurIPS/CVPR",
        ],
        "capability_profile": {
            "technical_depth": 0.96,
            "adaptability": 0.82,
            "leadership": 0.78,
            "execution": 0.89,
            "systems_thinking": 0.91,
            "creativity": 0.93,
            "resilience": 0.85,
            "communication": 0.80,
        }
    },
    {
        "name": "Rahul Verma",
        "email": "rahul.v@example.com",
        "headline": "Backend Engineer | 4 YOE | Recently Promoted | High Growth",
        "location": "Pune, India",
        "summary": (
            "4 years of experience but trajectory of someone with 10. "
            "Joined Razorpay as a junior, promoted 3 times in 3.5 years. "
            "Now leading a team of 5, building their payments reconciliation engine. "
            "Tier-2 college, no pedigree — pure output."
        ),
        "years_experience": 4.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech CS, VIT Vellore (2020)",
        "career_history": [
            {
                "company": "Razorpay",
                "industry": "Fintech",
                "company_size": "2500",
                "company_type": "startup-scale",
                "title": "Senior Software Engineer → Team Lead",
                "start_year": 2020,
                "end_year": 2024,
                "team_size": 5,
                "impact_score": 0.89,
                "description": "3 promotions in 3.5 years. Built reconciliation engine processing ₹2Cr/day."
            }
        ],
        "skills": [
            {"name": "Java", "proficiency": 0.88},
            {"name": "Kafka", "proficiency": 0.85},
            {"name": "MySQL", "proficiency": 0.82},
            {"name": "Spring Boot", "proficiency": 0.87},
            {"name": "System Design", "proficiency": 0.80},
        ],
        "achievements": [
            "3 promotions in 3.5 years at Razorpay",
            "Built reconciliation engine for ₹2Cr/day payment volume",
            "Onboarded and mentored 4 junior engineers",
        ],
        "capability_profile": {
            "technical_depth": 0.80,
            "adaptability": 0.88,
            "leadership": 0.82,
            "execution": 0.93,
            "systems_thinking": 0.79,
            "creativity": 0.75,
            "resilience": 0.90,
            "communication": 0.84,
        }
    },
    {
        "name": "Elena Vasquez",
        "email": "elena.v@example.com",
        "headline": "DevOps / Platform Engineer | 2-Year Career Gap (caretaker)",
        "location": "Mexico City, Mexico",
        "summary": (
            "8 years platform engineering experience. Took a 2-year career break to care for an ill parent. "
            "During the break: completed AWS Solutions Architect certification, contributed to Terraform providers. "
            "Previously built Mercado Libre's CI/CD platform used by 1200+ developers."
        ),
        "years_experience": 8.0,
        "education_tier": "tier2",
        "education_detail": "B.S. Systems Engineering, UNAM Mexico (2014)",
        "career_history": [
            {
                "company": "Career Break",
                "industry": "Personal",
                "company_size": "0",
                "company_type": "personal",
                "title": "Family caretaker + self-study",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 0,
                "impact_score": 0.0,
                "description": "Cared for ill parent. Earned AWS-SA cert. Terraform contributor."
            },
            {
                "company": "Mercado Libre",
                "industry": "E-commerce",
                "company_size": "20k+",
                "company_type": "enterprise",
                "title": "Staff Platform Engineer",
                "start_year": 2017,
                "end_year": 2022,
                "team_size": 10,
                "impact_score": 0.92,
                "description": "Built CI/CD platform for 1200 developers. Reduced deploy time from 45m to 8m."
            },
            {
                "company": "Despegar",
                "industry": "Travel Tech",
                "company_size": "1000",
                "company_type": "tech",
                "title": "DevOps Engineer",
                "start_year": 2014,
                "end_year": 2017,
                "team_size": 4,
                "impact_score": 0.78,
                "description": "Built observability stack. Automated infrastructure provisioning."
            }
        ],
        "skills": [
            {"name": "Terraform", "proficiency": 0.93},
            {"name": "AWS", "proficiency": 0.91},
            {"name": "Kubernetes", "proficiency": 0.90},
            {"name": "CI/CD", "proficiency": 0.94},
            {"name": "Python", "proficiency": 0.82},
            {"name": "Ansible", "proficiency": 0.85},
        ],
        "achievements": [
            "CI/CD platform serving 1200+ developers at Mercado Libre",
            "Reduced deployment time from 45 min to 8 min",
            "AWS Solutions Architect certified during career break",
        ],
        "capability_profile": {
            "technical_depth": 0.88,
            "adaptability": 0.90,
            "leadership": 0.80,
            "execution": 0.87,
            "systems_thinking": 0.89,
            "creativity": 0.76,
            "resilience": 0.97,
            "communication": 0.83,
        }
    },
    {
        "name": "Vikram Nair",
        "email": "vikram.n@example.com",
        "headline": "10x Bootcamp Grad | SWE @ Swiggy | 2 YOE",
        "location": "Chennai, India",
        "summary": (
            "Bootcamp graduate (Masai School) with 2 years at Swiggy. "
            "Top performer in every quarter. Built Swiggy's restaurant onboarding flow serving 250K restaurants. "
            "No CS degree but outperforms many IIT grads on the team per manager reviews."
        ),
        "years_experience": 2.0,
        "education_tier": "bootcamp",
        "education_detail": "Masai School Full-Stack Bootcamp (2022). B.Com, Loyola College (2020).",
        "career_history": [
            {
                "company": "Swiggy",
                "industry": "Food Tech",
                "company_size": "5000",
                "company_type": "startup-scale",
                "title": "Software Engineer",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 6,
                "impact_score": 0.83,
                "description": "Built restaurant onboarding flow. 250K restaurants. Top performer 4 quarters straight."
            }
        ],
        "skills": [
            {"name": "React", "proficiency": 0.85},
            {"name": "Node.js", "proficiency": 0.83},
            {"name": "MongoDB", "proficiency": 0.80},
            {"name": "Python", "proficiency": 0.72},
            {"name": "AWS", "proficiency": 0.70},
        ],
        "achievements": [
            "Top performer 4 consecutive quarters at Swiggy",
            "Built feature used by 250K restaurants",
            "Led migration from REST to GraphQL independently",
        ],
        "capability_profile": {
            "technical_depth": 0.72,
            "adaptability": 0.93,
            "leadership": 0.65,
            "execution": 0.91,
            "systems_thinking": 0.70,
            "creativity": 0.85,
            "resilience": 0.92,
            "communication": 0.80,
        }
    },
    {
        "name": "Ananya Krishnan",
        "email": "ananya.k@example.com",
        "headline": "Data Engineer | Ex-Amazon | Built ML Pipelines at Scale",
        "location": "Hyderabad, India",
        "summary": (
            "6 years data/ML engineering. Built Amazon Alexa's training data pipeline "
            "processing 2PB of audio data. Transitioned from pure data eng to ML platform engineering. "
            "Strong Python, Spark, Airflow expertise. Now building AI infra at a Series B startup."
        ),
        "years_experience": 6.0,
        "education_tier": "tier1",
        "education_detail": "B.Tech CS, NIT Trichy (2018)",
        "career_history": [
            {
                "company": "Sarvam AI",
                "industry": "AI",
                "company_size": "80",
                "company_type": "startup",
                "title": "ML Platform Engineer",
                "start_year": 2023,
                "end_year": 2024,
                "team_size": 4,
                "impact_score": 0.88,
                "description": "Building training infrastructure for India's LLM. Sole ML infra engineer."
            },
            {
                "company": "Amazon",
                "industry": "Big Tech",
                "company_size": "1M+",
                "company_type": "enterprise",
                "title": "Senior Data Engineer",
                "start_year": 2018,
                "end_year": 2023,
                "team_size": 9,
                "impact_score": 0.86,
                "description": "Alexa training data pipeline. 2PB audio data, 99.5% SLA."
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": 0.94},
            {"name": "Apache Spark", "proficiency": 0.92},
            {"name": "Airflow", "proficiency": 0.90},
            {"name": "AWS", "proficiency": 0.88},
            {"name": "dbt", "proficiency": 0.85},
            {"name": "Kafka", "proficiency": 0.82},
        ],
        "achievements": [
            "Alexa training pipeline processing 2PB of audio data",
            "Built ML training infra from scratch at Sarvam AI",
            "Open-source dbt plugin: 450 GitHub stars",
        ],
        "capability_profile": {
            "technical_depth": 0.88,
            "adaptability": 0.83,
            "leadership": 0.70,
            "execution": 0.90,
            "systems_thinking": 0.87,
            "creativity": 0.78,
            "resilience": 0.84,
            "communication": 0.77,
        }
    },
    {
        "name": "David Okafor",
        "email": "david.o@example.com",
        "headline": "Frontend → Fullstack | Career Switcher | 3 YOE",
        "location": "Nairobi, Kenya",
        "summary": (
            "Former civil engineer turned software developer. "
            "3 years of full-stack engineering at Safaricom and M-Pesa. "
            "Brings systems-level thinking from engineering background. "
            "Builds products that work for African internet conditions (low bandwidth, offline-first)."
        ),
        "years_experience": 3.0,
        "education_tier": "tier2",
        "education_detail": "B.Eng Civil Engineering, University of Nairobi (2016). Self-taught programmer.",
        "career_history": [
            {
                "company": "Safaricom / M-Pesa",
                "industry": "Telecom / Fintech",
                "company_size": "6000",
                "company_type": "enterprise",
                "title": "Software Engineer",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 5,
                "impact_score": 0.85,
                "description": "Built offline-first M-Pesa agent app. 50K daily active agents."
            },
            {
                "company": "Andela",
                "industry": "Tech Training",
                "company_size": "500",
                "company_type": "tech",
                "title": "Junior Developer",
                "start_year": 2020,
                "end_year": 2021,
                "team_size": 0,
                "impact_score": 0.70,
                "description": "Andela fellowship — top 3% cohort ranking."
            }
        ],
        "skills": [
            {"name": "React Native", "proficiency": 0.87},
            {"name": "Node.js", "proficiency": 0.82},
            {"name": "PostgreSQL", "proficiency": 0.78},
            {"name": "Offline-First Architecture", "proficiency": 0.90},
            {"name": "Python", "proficiency": 0.72},
        ],
        "achievements": [
            "Built offline-first M-Pesa agent app for 50K daily active agents",
            "Top 3% Andela fellowship cohort",
            "Patent pending: offline sync protocol for low-bandwidth environments",
        ],
        "capability_profile": {
            "technical_depth": 0.75,
            "adaptability": 0.92,
            "leadership": 0.68,
            "execution": 0.88,
            "systems_thinking": 0.85,
            "creativity": 0.90,
            "resilience": 0.93,
            "communication": 0.82,
        }
    },
    {
        "name": "Neha Patel",
        "email": "neha.p@example.com",
        "headline": "Engineering Manager | 8 YOE | P&G → Zepto | Leadership Track",
        "location": "Ahmedabad, India",
        "summary": (
            "8 years engineering, last 3 in management. Started as SWE at P&G's digital arm, "
            "moved to Zepto as one of their first engineering managers. "
            "Built and scaled a 25-person engineering org from 5. "
            "Strong product sense, excellent communicator, high-execution manager."
        ),
        "years_experience": 8.0,
        "education_tier": "tier1",
        "education_detail": "B.Tech CS, BITS Pilani (2016)",
        "career_history": [
            {
                "company": "Zepto",
                "industry": "Quick Commerce",
                "company_size": "2000",
                "company_type": "startup",
                "title": "Engineering Manager",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 25,
                "impact_score": 0.93,
                "description": "Scaled engineering org 5→25. Shipped 3 major product lines."
            },
            {
                "company": "P&G Digital",
                "industry": "FMCG Tech",
                "company_size": "90k+",
                "company_type": "enterprise",
                "title": "Senior Software Engineer",
                "start_year": 2016,
                "end_year": 2021,
                "team_size": 8,
                "impact_score": 0.80,
                "description": "Supply chain optimization system. $180M annual savings."
            }
        ],
        "skills": [
            {"name": "Engineering Management", "proficiency": 0.92},
            {"name": "Python", "proficiency": 0.82},
            {"name": "System Design", "proficiency": 0.85},
            {"name": "Product Management", "proficiency": 0.78},
            {"name": "Java", "proficiency": 0.75},
        ],
        "achievements": [
            "Scaled engineering team from 5 to 25 people",
            "Supply chain system saving $180M annually at P&G",
            "Launched 3 product lines shipping 10-minute delivery infrastructure",
        ],
        "capability_profile": {
            "technical_depth": 0.78,
            "adaptability": 0.88,
            "leadership": 0.95,
            "execution": 0.91,
            "systems_thinking": 0.84,
            "creativity": 0.80,
            "resilience": 0.87,
            "communication": 0.94,
        }
    },
    {
        "name": "Tom Bradley",
        "email": "tom.b@example.com",
        "headline": "Enterprise Java Developer | 12 YOE | IBM → Infosys",
        "location": "Bengaluru, India",
        "summary": (
            "12 years of Java enterprise development. Comfortable in large, well-defined systems. "
            "Has never built from scratch — always joining mature codebases. "
            "Deep knowledge of Spring ecosystem. Low risk tolerance. "
            "Excellent at maintenance and stability. Not a startup person."
        ),
        "years_experience": 12.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech CS, Anna University (2012)",
        "career_history": [
            {
                "company": "Infosys",
                "industry": "IT Services",
                "company_size": "300k+",
                "company_type": "enterprise",
                "title": "Senior Java Developer",
                "start_year": 2018,
                "end_year": 2024,
                "team_size": 20,
                "impact_score": 0.55,
                "description": "Maintained banking core system for Deutsche Bank. Stability-focused."
            },
            {
                "company": "IBM",
                "industry": "IT Services",
                "company_size": "300k+",
                "company_type": "enterprise",
                "title": "Java Developer",
                "start_year": 2012,
                "end_year": 2018,
                "team_size": 15,
                "impact_score": 0.50,
                "description": "Enterprise Java development for insurance clients."
            }
        ],
        "skills": [
            {"name": "Java", "proficiency": 0.90},
            {"name": "Spring Boot", "proficiency": 0.88},
            {"name": "Oracle DB", "proficiency": 0.82},
            {"name": "Maven", "proficiency": 0.85},
        ],
        "achievements": [
            "Zero production incidents for 3 consecutive years",
            "Maintained 99.9% uptime for Deutsche Bank system",
        ],
        "capability_profile": {
            "technical_depth": 0.80,
            "adaptability": 0.35,
            "leadership": 0.45,
            "execution": 0.78,
            "systems_thinking": 0.65,
            "creativity": 0.30,
            "resilience": 0.70,
            "communication": 0.60,
        }
    },
    {
        "name": "Zara Ahmed",
        "email": "zara.a@example.com",
        "headline": "ML Researcher → Engineer | NLP Specialist | Publish or Ship",
        "location": "Karachi, Pakistan",
        "summary": (
            "3 years ML research (2 NeurIPS papers) + 3 years industry ML engineering. "
            "Rare combination: can read papers AND ship production systems. "
            "Built Urdu/Hindi NLP models used by 40M users. "
            "Moved from pure research to product because 'impact matters more than citations.'"
        ),
        "years_experience": 6.0,
        "education_tier": "tier1",
        "education_detail": "M.S. AI, LUMS Pakistan (2018). Ex-research intern, Google Brain.",
        "career_history": [
            {
                "company": "Careem (Uber)",
                "industry": "Ride-hailing",
                "company_size": "5000",
                "company_type": "enterprise",
                "title": "Senior ML Engineer",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 6,
                "impact_score": 0.89,
                "description": "NLP models for Arabic/Urdu customer support. 40M users, $6M cost saved."
            },
            {
                "company": "LUMS AI Lab",
                "industry": "Research",
                "company_size": "20",
                "company_type": "academia",
                "title": "Research Engineer",
                "start_year": 2018,
                "end_year": 2021,
                "team_size": 5,
                "impact_score": 0.82,
                "description": "2 NeurIPS papers on multilingual NLP. Google Brain intern 2019."
            }
        ],
        "skills": [
            {"name": "NLP", "proficiency": 0.96},
            {"name": "PyTorch", "proficiency": 0.93},
            {"name": "Transformers", "proficiency": 0.95},
            {"name": "Python", "proficiency": 0.94},
            {"name": "MLOps", "proficiency": 0.80},
        ],
        "achievements": [
            "2 NeurIPS papers on multilingual NLP",
            "NLP system saving $6M/year at Careem",
            "Built first production-quality Urdu NLP model",
        ],
        "capability_profile": {
            "technical_depth": 0.95,
            "adaptability": 0.85,
            "leadership": 0.72,
            "execution": 0.83,
            "systems_thinking": 0.88,
            "creativity": 0.95,
            "resilience": 0.88,
            "communication": 0.78,
        }
    },
    {
        "name": "James Park",
        "email": "james.p@example.com",
        "headline": "Product Engineer | Figma → Linear | PLG Expert",
        "location": "Seoul, South Korea",
        "summary": (
            "5 years at design/dev tool companies. Built features used by millions of designers. "
            "Figma's collaborative editing infra, Linear's command palette + keyboard shortcuts. "
            "Obsessed with developer experience and zero-latency UI. "
            "Korean-American, Stanford CS grad."
        ),
        "years_experience": 5.0,
        "education_tier": "tier1",
        "education_detail": "B.S. Computer Science, Stanford University (2019)",
        "career_history": [
            {
                "company": "Linear",
                "industry": "Dev Tools",
                "company_size": "50",
                "company_type": "startup",
                "title": "Senior Software Engineer",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 3,
                "impact_score": 0.91,
                "description": "Command palette, keyboard nav, offline sync. Linear's 'snappy' reputation is partly my work."
            },
            {
                "company": "Figma",
                "industry": "Design Tools",
                "company_size": "800",
                "company_type": "startup",
                "title": "Software Engineer",
                "start_year": 2019,
                "end_year": 2022,
                "team_size": 5,
                "impact_score": 0.88,
                "description": "Collaborative editing conflict resolution. CRDT-based real-time sync."
            }
        ],
        "skills": [
            {"name": "TypeScript", "proficiency": 0.96},
            {"name": "React", "proficiency": 0.95},
            {"name": "WebAssembly", "proficiency": 0.85},
            {"name": "CRDTs", "proficiency": 0.88},
            {"name": "Rust", "proficiency": 0.80},
            {"name": "Performance Optimization", "proficiency": 0.94},
        ],
        "achievements": [
            "Built Figma's CRDT-based collaborative editing sync",
            "Linear command palette used by 200K+ teams",
            "Sub-16ms render time across entire Linear product",
        ],
        "capability_profile": {
            "technical_depth": 0.92,
            "adaptability": 0.86,
            "leadership": 0.70,
            "execution": 0.93,
            "systems_thinking": 0.88,
            "creativity": 0.91,
            "resilience": 0.82,
            "communication": 0.78,
        }
    },
    {
        "name": "Fatima Al-Rashidi",
        "email": "fatima.ar@example.com",
        "headline": "Security Engineer | Zero-Day Researcher | Bug Bounty Champion",
        "location": "Dubai, UAE",
        "summary": (
            "7 years in application security, specializing in finding and fixing critical vulnerabilities. "
            "$500K+ in bug bounty earnings from Meta, Google, and Microsoft. "
            "Built Careem's entire security engineering program from scratch. "
            "Teaches security at AUB. Self-taught — Computer Science degree but security is all self-learned."
        ),
        "years_experience": 7.0,
        "education_tier": "tier2",
        "education_detail": "B.S. Computer Science, American University of Beirut (2017)",
        "career_history": [
            {
                "company": "Careem",
                "industry": "Tech",
                "company_size": "5000",
                "company_type": "startup",
                "title": "Head of Security Engineering",
                "start_year": 2020,
                "end_year": 2024,
                "team_size": 8,
                "impact_score": 0.94,
                "description": "Built security program from scratch. Zero major breaches during tenure."
            },
            {
                "company": "Independent / Bug Bounty",
                "industry": "Security",
                "company_size": "1",
                "company_type": "freelance",
                "title": "Security Researcher",
                "start_year": 2017,
                "end_year": 2020,
                "team_size": 0,
                "impact_score": 0.90,
                "description": "$500K+ bounties. Critical vulnerabilities in Meta, Google, Microsoft products."
            }
        ],
        "skills": [
            {"name": "Penetration Testing", "proficiency": 0.96},
            {"name": "Application Security", "proficiency": 0.95},
            {"name": "Python", "proficiency": 0.85},
            {"name": "Rust", "proficiency": 0.80},
            {"name": "OWASP", "proficiency": 0.97},
            {"name": "Cryptography", "proficiency": 0.88},
        ],
        "achievements": [
            "$500K+ bug bounty earnings from Meta, Google, Microsoft",
            "Zero major security incidents in 4 years as Head of Security at Careem",
            "DEF CON speaker 2022",
        ],
        "capability_profile": {
            "technical_depth": 0.93,
            "adaptability": 0.82,
            "leadership": 0.80,
            "execution": 0.88,
            "systems_thinking": 0.90,
            "creativity": 0.92,
            "resilience": 0.88,
            "communication": 0.80,
        }
    },
    {
        "name": "Rohan Desai",
        "email": "rohan.d@example.com",
        "headline": "iOS Engineer | 5 YOE | Dunzo → Cred | Consumer Apps",
        "location": "Bengaluru, India",
        "summary": (
            "5 years iOS development at high-growth consumer apps. "
            "Built Dunzo's real-time delivery tracking used by 3M users. "
            "Now at Cred building premium fintech experiences. "
            "Strong product intuition, obsessed with performance and smoothness."
        ),
        "years_experience": 5.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech CS, Manipal Institute of Technology (2019)",
        "career_history": [
            {
                "company": "CRED",
                "industry": "Fintech",
                "company_size": "800",
                "company_type": "startup",
                "title": "iOS Engineer",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 4,
                "impact_score": 0.84,
                "description": "Built CRED's premium payment UX. 4.9 App Store rating maintained."
            },
            {
                "company": "Dunzo",
                "industry": "Quick Commerce",
                "company_size": "500",
                "company_type": "startup",
                "title": "iOS Developer",
                "start_year": 2019,
                "end_year": 2022,
                "team_size": 3,
                "impact_score": 0.82,
                "description": "Real-time delivery tracking. 3M users. Sub-100ms location updates."
            }
        ],
        "skills": [
            {"name": "Swift", "proficiency": 0.94},
            {"name": "SwiftUI", "proficiency": 0.90},
            {"name": "Core Animation", "proficiency": 0.88},
            {"name": "Instruments", "proficiency": 0.85},
            {"name": "WebRTC", "proficiency": 0.75},
        ],
        "achievements": [
            "Real-time delivery tracking for 3M Dunzo users",
            "4.9 App Store rating consistently maintained at CRED",
            "Reduced app startup time by 65% at Dunzo",
        ],
        "capability_profile": {
            "technical_depth": 0.85,
            "adaptability": 0.78,
            "leadership": 0.65,
            "execution": 0.90,
            "systems_thinking": 0.78,
            "creativity": 0.82,
            "resilience": 0.80,
            "communication": 0.74,
        }
    },
    {
        "name": "Aisha Okonkwo",
        "email": "aisha.o@example.com",
        "headline": "Data Scientist | Social Impact | Health Analytics",
        "location": "Accra, Ghana",
        "summary": (
            "5 years applying data science to healthcare and public health in Sub-Saharan Africa. "
            "Built predictive malaria outbreak model used by WHO field teams. "
            "Masters in Statistics from UCT. Rare combination of rigorous statistics and real-world deployment. "
            "Not a typical Bay Area candidate — and that is exactly the point."
        ),
        "years_experience": 5.0,
        "education_tier": "tier1",
        "education_detail": "M.S. Statistics, University of Cape Town (2019)",
        "career_history": [
            {
                "company": "WHO Africa",
                "industry": "Healthcare / NGO",
                "company_size": "500",
                "company_type": "ngo",
                "title": "Data Scientist",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 3,
                "impact_score": 0.95,
                "description": "Malaria outbreak predictor deployed in 7 countries. Estimated 40K lives impacted."
            },
            {
                "company": "mPharma",
                "industry": "HealthTech",
                "company_size": "200",
                "company_type": "startup",
                "title": "Junior Data Scientist",
                "start_year": 2019,
                "end_year": 2021,
                "team_size": 2,
                "impact_score": 0.80,
                "description": "Drug demand forecasting. Reduced medicine stockouts by 45%."
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": 0.90},
            {"name": "R", "proficiency": 0.92},
            {"name": "Statistical Modeling", "proficiency": 0.94},
            {"name": "Epidemiology", "proficiency": 0.88},
            {"name": "TensorFlow", "proficiency": 0.78},
        ],
        "achievements": [
            "Malaria predictor deployed across 7 WHO countries",
            "Estimated impact: 40K lives positively affected",
            "Nature Medicine paper on predictive disease surveillance",
        ],
        "capability_profile": {
            "technical_depth": 0.86,
            "adaptability": 0.90,
            "leadership": 0.75,
            "execution": 0.87,
            "systems_thinking": 0.85,
            "creativity": 0.88,
            "resilience": 0.94,
            "communication": 0.86,
        }
    },
    {
        "name": "Chen Wei",
        "email": "chen.w@example.com",
        "headline": "Backend Engineer | TikTok → ByteDance | Real-Time Systems",
        "location": "Shanghai, China",
        "summary": (
            "6 years at ByteDance building TikTok's content recommendation and live streaming infra. "
            "Systems that run at 100M+ concurrent users. "
            "Deep expertise in real-time data pipelines and low-latency architectures. "
            "Recently relocated — looking for next challenge outside ByteDance ecosystem."
        ),
        "years_experience": 6.0,
        "education_tier": "tier1",
        "education_detail": "B.Eng CS, Tsinghua University (2018)",
        "career_history": [
            {
                "company": "ByteDance / TikTok",
                "industry": "Social Media",
                "company_size": "100k+",
                "company_type": "enterprise",
                "title": "Senior Software Engineer",
                "start_year": 2018,
                "end_year": 2024,
                "team_size": 15,
                "impact_score": 0.91,
                "description": "Content recommendation serving 100M+ users. Live streaming infra. 5ms p99 latency."
            }
        ],
        "skills": [
            {"name": "Go", "proficiency": 0.93},
            {"name": "Kafka", "proficiency": 0.91},
            {"name": "Redis", "proficiency": 0.90},
            {"name": "Real-time Systems", "proficiency": 0.94},
            {"name": "C++", "proficiency": 0.80},
        ],
        "achievements": [
            "Real-time recommendation system for 100M+ concurrent TikTok users",
            "Achieved 5ms p99 latency on live streaming infra",
            "Led 3-person performance engineering team",
        ],
        "capability_profile": {
            "technical_depth": 0.94,
            "adaptability": 0.70,
            "leadership": 0.72,
            "execution": 0.91,
            "systems_thinking": 0.93,
            "creativity": 0.72,
            "resilience": 0.80,
            "communication": 0.65,
        }
    },
    {
        "name": "Pooja Iyer",
        "email": "pooja.i@example.com",
        "headline": "Product Manager turned SWE | 1 YOE | Late Bloomer",
        "location": "Bengaluru, India",
        "summary": (
            "Was a Product Manager for 5 years at Flipkart. "
            "Learned to code, switched to engineering. Now 1 year as SWE at a Series A startup. "
            "Unusual: deep product context + engineering capability. "
            "Writes code like a PM — always asking why before how."
        ),
        "years_experience": 1.0,
        "education_tier": "tier1",
        "education_detail": "MBA, IIM Bangalore (2017). Self-taught programmer from 2022.",
        "career_history": [
            {
                "company": "Classplus",
                "industry": "Edtech",
                "company_size": "300",
                "company_type": "startup",
                "title": "Software Engineer",
                "start_year": 2023,
                "end_year": 2024,
                "team_size": 5,
                "impact_score": 0.75,
                "description": "Full-stack feature development. Brought PM mindset to engineering. Shipped 5 features in 12 months."
            },
            {
                "company": "Flipkart",
                "industry": "E-commerce",
                "company_size": "20k+",
                "company_type": "enterprise",
                "title": "Product Manager",
                "start_year": 2017,
                "end_year": 2022,
                "team_size": 0,
                "impact_score": 0.82,
                "description": "Led search & discovery PM. Feature shipped to 200M users."
            }
        ],
        "skills": [
            {"name": "React", "proficiency": 0.72},
            {"name": "Node.js", "proficiency": 0.68},
            {"name": "Python", "proficiency": 0.70},
            {"name": "Product Strategy", "proficiency": 0.93},
            {"name": "Data Analysis", "proficiency": 0.85},
        ],
        "achievements": [
            "Successful PM→SWE career switch",
            "Led Flipkart search product used by 200M users",
            "Built and shipped 5 features in first year as engineer",
        ],
        "capability_profile": {
            "technical_depth": 0.65,
            "adaptability": 0.97,
            "leadership": 0.85,
            "execution": 0.85,
            "systems_thinking": 0.82,
            "creativity": 0.88,
            "resilience": 0.95,
            "communication": 0.95,
        }
    },
    {
        "name": "Alex Rivera",
        "email": "alex.r@example.com",
        "headline": "Founding Engineer | 2 YOE at Seed Startup | Builder",
        "location": "Buenos Aires, Argentina",
        "summary": (
            "Founding engineer at a seed-stage climate tech startup. "
            "Joined as employee #2. Built the entire product stack from scratch. "
            "Wears 5 hats: backend, frontend, data, devops, and sometimes customer support. "
            "IIT-level talent in a country nobody searches."
        ),
        "years_experience": 2.5,
        "education_tier": "tier2",
        "education_detail": "B.S. Systems Engineering, UBA Argentina (2021)",
        "career_history": [
            {
                "company": "Carbontrack (Seed Stage)",
                "industry": "Climate Tech",
                "company_size": "5",
                "company_type": "startup",
                "title": "Founding Engineer",
                "start_year": 2022,
                "end_year": 2024,
                "team_size": 2,
                "impact_score": 0.90,
                "description": "Built entire product from 0. Carbon tracking SaaS. $1.2M ARR in 18 months."
            }
        ],
        "skills": [
            {"name": "Python", "proficiency": 0.88},
            {"name": "React", "proficiency": 0.85},
            {"name": "AWS", "proficiency": 0.82},
            {"name": "PostgreSQL", "proficiency": 0.83},
            {"name": "FastAPI", "proficiency": 0.86},
        ],
        "achievements": [
            "Built entire SaaS product from scratch as employee #2",
            "$1.2M ARR in 18 months",
            "Product used by 150 enterprise climate teams",
        ],
        "capability_profile": {
            "technical_depth": 0.80,
            "adaptability": 0.96,
            "leadership": 0.78,
            "execution": 0.95,
            "systems_thinking": 0.82,
            "creativity": 0.88,
            "resilience": 0.94,
            "communication": 0.80,
        }
    },
    {
        "name": "Siddharth Malhotra",
        "email": "sid.m@example.com",
        "headline": "Senior SWE | 6 YOE | Average Trajectory | Stable Performer",
        "location": "Noida, India",
        "summary": (
            "6 years of consistent software engineering. Good team player. "
            "Delivers tasks reliably. Not a rockstar but never a blocker. "
            "Mid-level performer at mid-size companies. "
            "Would do well in a defined role with clear scope."
        ),
        "years_experience": 6.0,
        "education_tier": "tier2",
        "education_detail": "B.Tech CS, Amity University (2018)",
        "career_history": [
            {
                "company": "Persistent Systems",
                "industry": "IT Services",
                "company_size": "20k+",
                "company_type": "enterprise",
                "title": "Senior Software Engineer",
                "start_year": 2021,
                "end_year": 2024,
                "team_size": 10,
                "impact_score": 0.60,
                "description": "Backend development for banking client. Maintains existing services."
            },
            {
                "company": "HCL Technologies",
                "industry": "IT Services",
                "company_size": "200k+",
                "company_type": "enterprise",
                "title": "Software Engineer",
                "start_year": 2018,
                "end_year": 2021,
                "team_size": 12,
                "impact_score": 0.55,
                "description": "Java development. Project delivery on time."
            }
        ],
        "skills": [
            {"name": "Java", "proficiency": 0.78},
            {"name": "Spring Boot", "proficiency": 0.75},
            {"name": "MySQL", "proficiency": 0.72},
            {"name": "REST APIs", "proficiency": 0.76},
        ],
        "achievements": [
            "Delivered 12 sprint milestones on time",
            "Awarded 'reliable performer' by Persistent Systems",
        ],
        "capability_profile": {
            "technical_depth": 0.68,
            "adaptability": 0.55,
            "leadership": 0.45,
            "execution": 0.72,
            "systems_thinking": 0.58,
            "creativity": 0.42,
            "resilience": 0.65,
            "communication": 0.62,
        }
    },
]

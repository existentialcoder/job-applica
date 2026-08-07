"""
Generate ~100 diversified dummy job-application records as JSON.

Pure stdlib, no DB/app imports — run with any Python 3.11+, no venv required:
    python3 scripts/generate_dummy_jobs.py [--count 100] [--seed 42] [--out scripts/dummy_jobs.json]

Output feeds scripts/seed_dummy_jobs.py, which inserts the records into Postgres.
"""
import argparse
import json
import random
from datetime import date, datetime, timedelta

COMPANIES = [
    {"name": "Nimbus Cloud", "industry": "Cloud Infrastructure", "size": 450},
    {"name": "Voltra Energy", "industry": "Clean Energy", "size": 1200},
    {"name": "Pixelforge Studios", "industry": "Gaming", "size": 220},
    {"name": "Ledgerly", "industry": "Fintech", "size": 90},
    {"name": "Northwind Logistics", "industry": "Supply Chain", "size": 3400},
    {"name": "Brightpath Health", "industry": "Healthtech", "size": 600},
    {"name": "Quanta Robotics", "industry": "Robotics", "size": 310},
    {"name": "Cinderline Retail", "industry": "E-commerce", "size": 5200},
    {"name": "Fablehaus", "industry": "Media & Entertainment", "size": 150},
    {"name": "Substratum Data", "industry": "Data Infrastructure", "size": 80},
    {"name": "Orbital Freight", "industry": "Aerospace", "size": 2100},
    {"name": "Kindling Labs", "industry": "EdTech", "size": 60},
    {"name": "Greenhouse Metrics", "industry": "AgTech", "size": 130},
    {"name": "Ferrovia Systems", "industry": "Transportation", "size": 900},
    {"name": "Hearth Financial", "industry": "Fintech", "size": 700},
    {"name": "Wren & Co", "industry": "Design", "size": 40},
    {"name": "Palisade Security", "industry": "Cybersecurity", "size": 260},
    {"name": "Momentum Analytics", "industry": "AI / Analytics", "size": 190},
    {"name": "Slateworks", "industry": "Developer Tools", "size": 75},
    {"name": "Coral Reef Studios", "industry": "Marketing", "size": 55},
    {"name": "Basalt Manufacturing", "industry": "Manufacturing", "size": 4800},
    {"name": "Tidewater Biotech", "industry": "Biotech", "size": 340},
    {"name": "Auric Trading", "industry": "Financial Services", "size": 1800},
    {"name": "Meridian Health Group", "industry": "Healthcare", "size": 6200},
    {"name": "Fenwick Realty Tech", "industry": "PropTech", "size": 120},
    {"name": "Cascade Freight Co", "industry": "Logistics", "size": 1500},
    {"name": "Verdant Foods", "industry": "AgTech", "size": 800},
    {"name": "Ironclad Insurance", "industry": "Insurance", "size": 2600},
    {"name": "Lumenary Optics", "industry": "Hardware", "size": 210},
    {"name": "Driftwood Travel", "industry": "Travel Tech", "size": 175},
    {"name": "Bastion Networks", "industry": "Telecom", "size": 1900},
    {"name": "Rivergate Studios", "industry": "Gaming", "size": 95},
    {"name": "Solace Wellness", "industry": "Healthtech", "size": 260},
    {"name": "Vantage Point Consulting", "industry": "Consulting", "size": 3100},
    {"name": "Nightowl Media", "industry": "Media & Entertainment", "size": 68},
]

JOB_TITLES = [
    ("Software Engineer", "Engineering"),
    ("Senior Software Engineer", "Engineering"),
    ("Staff Software Engineer", "Engineering"),
    ("Backend Engineer", "Engineering"),
    ("Frontend Engineer", "Engineering"),
    ("Full Stack Engineer", "Engineering"),
    ("Platform Engineer", "Engineering"),
    ("Site Reliability Engineer", "Engineering"),
    ("DevOps Engineer", "Engineering"),
    ("Mobile Engineer (iOS)", "Engineering"),
    ("Mobile Engineer (Android)", "Engineering"),
    ("Data Engineer", "Data"),
    ("Data Scientist", "Data"),
    ("Machine Learning Engineer", "Data"),
    ("Analytics Engineer", "Data"),
    ("Product Manager", "Product"),
    ("Senior Product Manager", "Product"),
    ("Technical Product Manager", "Product"),
    ("Product Designer", "Design"),
    ("UX Researcher", "Design"),
    ("Engineering Manager", "Engineering"),
    ("QA Engineer", "Engineering"),
    ("Solutions Architect", "Engineering"),
    ("Security Engineer", "Engineering"),
    ("Technical Writer", "Documentation"),
    ("Sales Engineer", "Sales"),
    ("Account Executive", "Sales"),
    ("Customer Success Manager", "Customer Success"),
    ("Marketing Manager", "Marketing"),
    ("Growth Marketer", "Marketing"),
    ("Recruiter", "People"),
    ("Business Analyst", "Operations"),
    ("Operations Manager", "Operations"),
]

LOCATIONS = [
    # United States
    {"city": "San Francisco", "state": "CA", "country": "United States"},
    {"city": "Los Angeles", "state": "CA", "country": "United States"},
    {"city": "New York", "state": "NY", "country": "United States"},
    {"city": "Austin", "state": "TX", "country": "United States"},
    {"city": "Dallas", "state": "TX", "country": "United States"},
    {"city": "Seattle", "state": "WA", "country": "United States"},
    {"city": "Denver", "state": "CO", "country": "United States"},
    {"city": "Chicago", "state": "IL", "country": "United States"},
    {"city": "Boston", "state": "MA", "country": "United States"},
    {"city": "Miami", "state": "FL", "country": "United States"},
    {"city": "Atlanta", "state": "GA", "country": "United States"},
    {"city": "Raleigh", "state": "NC", "country": "United States"},
    {"city": "Phoenix", "state": "AZ", "country": "United States"},
    {"city": "Portland", "state": "OR", "country": "United States"},
    {"city": "Minneapolis", "state": "MN", "country": "United States"},
    {"city": "Salt Lake City", "state": "UT", "country": "United States"},
    # Canada
    {"city": "Toronto", "state": "ON", "country": "Canada"},
    {"city": "Vancouver", "state": "BC", "country": "Canada"},
    {"city": "Montreal", "state": "QC", "country": "Canada"},
    {"city": "Calgary", "state": "AB", "country": "Canada"},
    # Europe
    {"city": "Berlin", "state": None, "country": "Germany"},
    {"city": "Munich", "state": None, "country": "Germany"},
    {"city": "Hamburg", "state": None, "country": "Germany"},
    {"city": "Amsterdam", "state": None, "country": "Netherlands"},
    {"city": "Rotterdam", "state": None, "country": "Netherlands"},
    {"city": "London", "state": None, "country": "United Kingdom"},
    {"city": "Manchester", "state": None, "country": "United Kingdom"},
    {"city": "Edinburgh", "state": None, "country": "United Kingdom"},
    {"city": "Dublin", "state": None, "country": "Ireland"},
    {"city": "Lisbon", "state": None, "country": "Portugal"},
    {"city": "Porto", "state": None, "country": "Portugal"},
    {"city": "Barcelona", "state": None, "country": "Spain"},
    {"city": "Madrid", "state": None, "country": "Spain"},
    {"city": "Paris", "state": None, "country": "France"},
    {"city": "Lyon", "state": None, "country": "France"},
    {"city": "Stockholm", "state": None, "country": "Sweden"},
    {"city": "Copenhagen", "state": None, "country": "Denmark"},
    {"city": "Oslo", "state": None, "country": "Norway"},
    {"city": "Helsinki", "state": None, "country": "Finland"},
    {"city": "Zurich", "state": None, "country": "Switzerland"},
    {"city": "Vienna", "state": None, "country": "Austria"},
    {"city": "Warsaw", "state": None, "country": "Poland"},
    {"city": "Krakow", "state": None, "country": "Poland"},
    {"city": "Prague", "state": None, "country": "Czech Republic"},
    {"city": "Bucharest", "state": None, "country": "Romania"},
    {"city": "Milan", "state": None, "country": "Italy"},
    {"city": "Athens", "state": None, "country": "Greece"},
    # Asia-Pacific
    {"city": "Bangalore", "state": "Karnataka", "country": "India"},
    {"city": "Hyderabad", "state": "Telangana", "country": "India"},
    {"city": "Pune", "state": "Maharashtra", "country": "India"},
    {"city": "Singapore", "state": None, "country": "Singapore"},
    {"city": "Tokyo", "state": None, "country": "Japan"},
    {"city": "Osaka", "state": None, "country": "Japan"},
    {"city": "Seoul", "state": None, "country": "South Korea"},
    {"city": "Hong Kong", "state": None, "country": "Hong Kong"},
    {"city": "Taipei", "state": None, "country": "Taiwan"},
    {"city": "Sydney", "state": "NSW", "country": "Australia"},
    {"city": "Melbourne", "state": "VIC", "country": "Australia"},
    {"city": "Brisbane", "state": "QLD", "country": "Australia"},
    {"city": "Auckland", "state": None, "country": "New Zealand"},
    {"city": "Manila", "state": None, "country": "Philippines"},
    {"city": "Jakarta", "state": None, "country": "Indonesia"},
    # Latin America
    {"city": "Sao Paulo", "state": None, "country": "Brazil"},
    {"city": "Rio de Janeiro", "state": None, "country": "Brazil"},
    {"city": "Mexico City", "state": None, "country": "Mexico"},
    {"city": "Buenos Aires", "state": None, "country": "Argentina"},
    {"city": "Bogota", "state": None, "country": "Colombia"},
    {"city": "Santiago", "state": None, "country": "Chile"},
    # Middle East & Africa
    {"city": "Dubai", "state": None, "country": "United Arab Emirates"},
    {"city": "Tel Aviv", "state": None, "country": "Israel"},
    {"city": "Cape Town", "state": None, "country": "South Africa"},
    {"city": "Johannesburg", "state": None, "country": "South Africa"},
    {"city": "Nairobi", "state": None, "country": "Kenya"},
    {"city": "Lagos", "state": None, "country": "Nigeria"},
]

SKILL_POOL = [
    ("python", "Python"), ("typescript", "TypeScript"), ("javascript", "JavaScript"),
    ("go", "Go"), ("rust", "Rust"), ("java", "Java"), ("kotlin", "Kotlin"),
    ("vue", "Vue.js"), ("react", "React"), ("nodejs", "Node.js"), ("fastapi", "FastAPI"),
    ("django", "Django"), ("postgresql", "PostgreSQL"), ("mysql", "MySQL"),
    ("redis", "Redis"), ("kafka", "Kafka"), ("docker", "Docker"), ("kubernetes", "Kubernetes"),
    ("aws", "AWS"), ("gcp", "GCP"), ("azure", "Azure"), ("terraform", "Terraform"),
    ("graphql", "GraphQL"), ("rest_apis", "REST APIs"), ("grpc", "gRPC"),
    ("machine_learning", "Machine Learning"), ("pytorch", "PyTorch"), ("tensorflow", "TensorFlow"),
    ("sql", "SQL"), ("spark", "Apache Spark"), ("airflow", "Airflow"),
    ("figma", "Figma"), ("user_research", "User Research"), ("ab_testing", "A/B Testing"),
    ("salesforce", "Salesforce"), ("hubspot", "HubSpot"), ("seo", "SEO"),
    ("agile", "Agile / Scrum"), ("jira", "Jira"), ("ci_cd", "CI/CD"), ("linux", "Linux"),
]

WORK_MODELS = ["On-site", "Remote", "Hybrid"]
POSITIONS = ["Intern", "Junior", "Mid", "Senior", "Lead", "Manager"]
SOURCE_PLATFORMS = ["LinkedIn", "Indeed", "Glassdoor", "Monster", "ZipRecruiter", "Jobscan", "Other", None]

# Board-stage keys a seeded job can land on, weighted toward the earlier funnel stages
# (mirrors models/board.py DEFAULT_STAGES) — the loader maps these onto the target user's boards.
STAGE_WEIGHTS = [
    ("Saved", 30), ("Applied", 26), ("Phone Screen", 14), ("Interview", 12),
    ("Offer", 6), ("Accepted", 3), ("Rejected", 12), ("Withdrawn", 4),
    ("Ghosted", 6), ("Archived", 3),
]

SALARY_FORMATS = [
    lambda: f"${random.randint(70, 220)}k - ${random.randint(230, 320)}k",
    lambda: f"${random.randint(28, 95)}/hr",
    lambda: f"€{random.randint(55, 140)}k - €{random.randint(145, 190)}k",
    lambda: f"£{random.randint(45, 130)}k",
    lambda: None,
    lambda: None,
]

DESCRIPTION_TEMPLATES = [
    "We're looking for a {title} to join our {industry} team. You'll work closely with "
    "cross-functional partners to ship high-impact features, own critical systems end to end, "
    "and help define technical direction as we scale.",
    "As a {title} at {company}, you will design, build, and maintain systems that power our "
    "{industry} platform. We value ownership, pragmatism, and clear communication over process "
    "for its own sake.",
    "{company} is hiring a {title} to help us grow our {industry} offering. Ideal candidates "
    "are comfortable with ambiguity, enjoy mentoring others, and can balance speed with quality.",
    None,
    None,
]

NOTES_POOL = [
    "Referred by a former colleague — following up next week.",
    "Recruiter reached out on LinkedIn first.",
    "Great culture fit based on the initial call.",
    "Compensation is slightly below target range.",
    "Waiting to hear back after final round.",
    None, None, None,
]


def weighted_choice(weighted_pairs):
    items, weights = zip(*weighted_pairs)
    return random.choices(items, weights=weights, k=1)[0]


def random_date_within(days_back: int) -> date:
    return date.today() - timedelta(days=random.randint(0, days_back))


def build_company(base: dict) -> dict:
    slug = base["name"].lower().replace(" & ", "-").replace(" ", "-").replace(".", "")
    return {
        "name": base["name"],
        "website": f"https://www.{slug}.com",
        "email": None,
        "size": base["size"],
        "industry": base["industry"],
        "description": f"{base['name']} is a {base['industry'].lower()} company.",
        "logo_url": None,
    }


def build_skills(count: int) -> list[dict]:
    chosen = random.sample(SKILL_POOL, k=min(count, len(SKILL_POOL)))
    return [{"name": name, "label": label} for name, label in chosen]


def build_years_of_experience() -> dict | None:
    if random.random() < 0.35:
        return None
    lo = random.choice([0, 1, 2, 3, 4, 5])
    hi = lo + random.choice([2, 3, 4, 5])
    return {"min": lo, "max": hi}


SUGGESTION_POOL = [
    "Quantify your impact with concrete metrics (e.g. throughput, latency, cost savings) instead of describing responsibilities alone.",
    "Move your most relevant recent experience higher up — the top third of the resume gets the most attention.",
    "Add a short summary tailored to this role's core requirements at the top of your resume.",
    "List specific tools and versions you've used rather than broad category names.",
    "Highlight any leadership or mentoring experience if you're targeting a senior-level role.",
    "Trim unrelated older experience to keep the resume focused on relevant skills.",
    "Call out any certifications or courses related to the missing skills below.",
]


def build_ats(has_score: bool) -> tuple[float | None, dict | None]:
    if not has_score:
        return None, None
    score = round(random.uniform(35, 98), 1)
    report = {
        "score": score,
        "matched_skills": random.sample([s[1] for s in SKILL_POOL], k=random.randint(3, 8)),
        "missing_skills": random.sample([s[1] for s in SKILL_POOL], k=random.randint(0, 4)),
        "suggestions": random.sample(SUGGESTION_POOL, k=random.randint(1, 3)),
        "resume_id": None,  # filled in by seed_dummy_jobs.py once a real resume is assigned
    }
    return score, report


def build_job(index: int) -> dict:
    company_base = random.choice(COMPANIES)
    title, category = random.choice(JOB_TITLES)
    location = random.choice(LOCATIONS)
    work_model = random.choice(WORK_MODELS)
    if work_model == "Remote" and random.random() < 0.3:
        location = {"city": None, "state": None, "country": location["country"]}

    stage_key = weighted_choice(STAGE_WEIGHTS)
    created = random_date_within(150)
    applied_date = None
    if stage_key != "Saved":
        applied_date = (created + timedelta(days=random.randint(0, 10))).isoformat()

    has_ats_score = random.random() < 0.55
    ats_score, ats_report = build_ats(has_ats_score)

    salary_fn = random.choice(SALARY_FORMATS)
    description_template = random.choice(DESCRIPTION_TEMPLATES)
    description = (
        description_template.format(title=title, company=company_base["name"], industry=company_base["industry"])
        if description_template
        else None
    )

    return {
        "title": title,
        "category": category,
        "company": build_company(company_base),
        "location": location,
        "stage_key": stage_key,  # resolved to a real board status by the loader
        "position": random.choice(POSITIONS),
        "salary_range": salary_fn(),
        "work_model": work_model,
        "required_skills": build_skills(random.randint(0, 6)),
        "description": description,
        "years_of_experience": build_years_of_experience(),
        "source_url": f"https://jobs.example.com/{company_base['name'].lower().replace(' ', '-')}/{index}",
        "source_platform": random.choice(SOURCE_PLATFORMS),
        "applied_date": applied_date,
        "notes": random.choice(NOTES_POOL),
        "ats_score": ats_score,
        "ats_report": ats_report,
        "created_at": created.isoformat(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", default="scripts/dummy_jobs.json")
    args = parser.parse_args()

    random.seed(args.seed)
    jobs = [build_job(i) for i in range(1, args.count + 1)]

    with open(args.out, "w") as f:
        json.dump(jobs, f, indent=2, default=str)

    print(f"Wrote {len(jobs)} dummy jobs to {args.out}")


if __name__ == "__main__":
    main()

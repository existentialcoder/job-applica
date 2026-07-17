"""Seed comprehensive skills list (LinkedIn-style, 700+ entries)

Revision ID: a9f3e2c1b874
Revises: 4cbb352d4755
Create Date: 2026-07-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'a9f3e2c1b874'
down_revision: Union[str, Sequence[str], None] = '4cbb352d4755'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# fmt: off
_SKILLS: list[str] = [
    # ── Programming Languages ──────────────────────────────────────────────────
    'Python', 'JavaScript', 'TypeScript', 'Java', 'C', 'C++', 'C#', 'Go',
    'Rust', 'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB', 'Perl',
    'Lua', 'Haskell', 'Clojure', 'Erlang', 'Elixir', 'F#', 'Dart', 'Julia',
    'Bash', 'PowerShell', 'Visual Basic', 'COBOL', 'Fortran', 'Assembly',
    'Groovy', 'Objective-C', 'Verilog', 'VHDL', 'Prolog', 'Lisp', 'OCaml',
    'Nim', 'Zig', 'Crystal', 'Racket', 'Ada', 'Solidity', 'Move', 'Cairo',
    'Apex', 'PL/SQL', 'T-SQL', 'CoffeeScript', 'Elm', 'PureScript',

    # ── Frontend Frameworks & Libraries ───────────────────────────────────────
    'React', 'Vue.js', 'Angular', 'Svelte', 'Next.js', 'Nuxt.js', 'Remix',
    'Astro', 'Ember.js', 'Backbone.js', 'jQuery', 'Alpine.js', 'Lit',
    'Solid.js', 'Qwik', 'Preact', 'Marko', 'Stimulus',

    # ── Frontend Tools & Styling ───────────────────────────────────────────────
    'HTML5', 'CSS3', 'Sass', 'Less', 'Tailwind CSS', 'Bootstrap',
    'Material UI', 'Chakra UI', 'Ant Design', 'Radix UI', 'Styled Components',
    'Webpack', 'Vite', 'Rollup', 'Parcel', 'esbuild', 'Turbopack',
    'Babel', 'ESLint', 'Prettier', 'Storybook',

    # ── Data Visualisation (Frontend) ─────────────────────────────────────────
    'D3.js', 'Chart.js', 'Three.js', 'Framer Motion', 'GSAP', 'Highcharts',
    'ECharts', 'Recharts', 'Victory',

    # ── Backend Frameworks ─────────────────────────────────────────────────────
    'FastAPI', 'Django', 'Flask', 'Express.js', 'NestJS', 'Spring Boot',
    'Ruby on Rails', 'Laravel', 'Symfony', 'ASP.NET Core', 'Gin', 'Echo',
    'Fiber', 'Actix', 'Rocket', 'Axum', 'Phoenix', 'Sinatra', 'Hapi.js',
    'Koa.js', 'Fastify', 'Tornado', 'Falcon', 'Sanic', 'Lumen', 'Slim',
    'Micronaut', 'Quarkus', 'Ktor', 'Beego', 'Buffalo', 'Gorilla Mux',

    # ── Relational Databases ───────────────────────────────────────────────────
    'PostgreSQL', 'MySQL', 'SQLite', 'MariaDB', 'Oracle Database',
    'Microsoft SQL Server', 'CockroachDB', 'SingleStore', 'PlanetScale',
    'Supabase', 'Neon',

    # ── NoSQL Databases ────────────────────────────────────────────────────────
    'MongoDB', 'Cassandra', 'Couchbase', 'CouchDB', 'DynamoDB', 'Redis',
    'Memcached', 'Apache HBase', 'RethinkDB', 'FaunaDB', 'Firestore',
    'ArangoDB', 'Aerospike',

    # ── Time-Series & Analytics Databases ─────────────────────────────────────
    'InfluxDB', 'TimescaleDB', 'ClickHouse', 'Snowflake', 'BigQuery',
    'Amazon Redshift', 'Databricks', 'Apache Druid', 'Apache Pinot',
    'Dremio', 'Starburst',

    # ── Vector Databases ───────────────────────────────────────────────────────
    'Pinecone', 'Weaviate', 'Chroma', 'Milvus', 'pgvector', 'Qdrant',
    'Zilliz',

    # ── Search ────────────────────────────────────────────────────────────────
    'Elasticsearch', 'OpenSearch', 'Algolia', 'Meilisearch', 'Typesense',
    'Apache Solr',

    # ── Cloud Platforms ───────────────────────────────────────────────────────
    'AWS', 'Google Cloud Platform', 'Microsoft Azure', 'Cloudflare',
    'DigitalOcean', 'Heroku', 'Vercel', 'Netlify', 'Fly.io', 'Render',
    'Railway', 'Linode', 'Vultr', 'IBM Cloud', 'Oracle Cloud',
    'Alibaba Cloud', 'OVHcloud', 'Hetzner',

    # ── AWS Services ──────────────────────────────────────────────────────────
    'Amazon EC2', 'Amazon S3', 'Amazon RDS', 'AWS Lambda', 'Amazon ECS',
    'Amazon EKS', 'Amazon SQS', 'Amazon SNS', 'Amazon CloudFront',
    'Amazon Route 53', 'Amazon VPC', 'AWS IAM', 'Amazon CloudWatch',
    'Amazon Kinesis', 'AWS Glue', 'Amazon EMR', 'AWS Step Functions',
    'Amazon API Gateway', 'AWS AppSync', 'Amazon Cognito',
    'AWS Secrets Manager', 'AWS CloudFormation', 'AWS CDK', 'AWS SAM',

    # ── GCP Services ──────────────────────────────────────────────────────────
    'Google Kubernetes Engine', 'Google Cloud Run', 'Google Cloud Functions',
    'Google Cloud Storage', 'Google Cloud SQL', 'Vertex AI', 'Google Pub/Sub',
    'BigTable', 'Firebase',

    # ── Azure Services ────────────────────────────────────────────────────────
    'Azure Kubernetes Service', 'Azure Functions', 'Azure Blob Storage',
    'Azure Cosmos DB', 'Azure Service Bus', 'Azure DevOps', 'Azure AD',
    'Azure App Service', 'Azure Container Instances',

    # ── DevOps / Containers ───────────────────────────────────────────────────
    'Docker', 'Kubernetes', 'Helm', 'Docker Compose', 'Podman', 'containerd',

    # ── Infrastructure as Code ────────────────────────────────────────────────
    'Terraform', 'Ansible', 'Puppet', 'Chef', 'SaltStack', 'Pulumi',
    'Vagrant', 'Packer',

    # ── CI/CD ─────────────────────────────────────────────────────────────────
    'Jenkins', 'GitHub Actions', 'GitLab CI', 'CircleCI', 'Travis CI',
    'Bitbucket Pipelines', 'TeamCity', 'Bamboo', 'ArgoCD', 'Flux',
    'Tekton', 'Drone CI', 'Spinnaker', 'GoCD',

    # ── Observability / Monitoring ────────────────────────────────────────────
    'Prometheus', 'Grafana', 'Datadog', 'New Relic', 'PagerDuty', 'Sentry',
    'Jaeger', 'Zipkin', 'OpenTelemetry', 'ELK Stack', 'Loki', 'Tempo',
    'Dynatrace', 'AppDynamics', 'Splunk', 'Honeycomb',

    # ── Web Servers / Proxies ─────────────────────────────────────────────────
    'Nginx', 'Apache HTTP Server', 'HAProxy', 'Traefik', 'Envoy', 'Caddy',

    # ── Service Mesh / Discovery ──────────────────────────────────────────────
    'Istio', 'Consul', 'HashiCorp Vault', 'etcd', 'ZooKeeper', 'Linkerd',
    'Kuma',

    # ── Messaging / Streaming ─────────────────────────────────────────────────
    'Apache Kafka', 'RabbitMQ', 'Apache Pulsar', 'NATS', 'Apache ActiveMQ',
    'Celery', 'BullMQ', 'Socket.io', 'Redis Pub/Sub',

    # ── Mobile ────────────────────────────────────────────────────────────────
    'React Native', 'Flutter', 'SwiftUI', 'Jetpack Compose', 'Xamarin',
    'Ionic', 'Cordova', 'Capacitor', 'Expo', 'Android SDK', 'iOS SDK',
    'RevenueCat', 'XCTest', 'Espresso', 'Detox', 'App Center',
    'Push Notifications', 'Core Data', 'Room Database',

    # ── Data Science / ML / AI Frameworks ────────────────────────────────────
    'NumPy', 'Pandas', 'Matplotlib', 'Seaborn', 'Plotly', 'Scikit-learn',
    'SciPy', 'TensorFlow', 'PyTorch', 'Keras', 'JAX', 'Hugging Face',
    'LangChain', 'LlamaIndex', 'OpenAI API', 'Anthropic API',
    'XGBoost', 'LightGBM', 'CatBoost', 'OpenCV', 'NLTK', 'spaCy',
    'Gensim', 'Stable Diffusion', 'YOLO', 'Transformers',
    'Sentence Transformers', 'Einops', 'Accelerate', 'PEFT', 'DeepSpeed',
    'vLLM', 'llama.cpp',

    # ── MLOps / Data Engineering ──────────────────────────────────────────────
    'MLflow', 'Weights & Biases', 'DVC', 'Apache Spark', 'Apache Flink',
    'Apache Beam', 'Apache Hadoop', 'Apache Hive', 'Apache Airflow',
    'Prefect', 'Dagster', 'dbt', 'Great Expectations', 'Feast',
    'Dask', 'Ray', 'Polars', 'Apache Kafka Streams', 'Delta Lake',
    'Apache Iceberg', 'Apache Hudi', 'Fivetran', 'Airbyte',
    'Stitch', 'Apache NiFi',

    # ── BI / Visualisation ────────────────────────────────────────────────────
    'Tableau', 'Power BI', 'Metabase', 'Apache Superset', 'Redash', 'Looker',
    'Google Looker Studio', 'Streamlit', 'Gradio', 'Dash',

    # ── Analytics & Product Analytics ─────────────────────────────────────────
    'Google Analytics', 'Amplitude', 'Mixpanel', 'Segment', 'Heap Analytics',
    'FullStory', 'Hotjar', 'PostHog',

    # ── Testing ───────────────────────────────────────────────────────────────
    'Jest', 'Vitest', 'Mocha', 'Chai', 'Jasmine', 'Karma',
    'Cypress', 'Playwright', 'Selenium', 'Puppeteer', 'WebdriverIO',
    'pytest', 'unittest', 'JUnit', 'TestNG', 'Mockito',
    'PHPUnit', 'RSpec', 'Minitest', 'Factory Bot',
    'Artillery', 'k6', 'Locust', 'Gatling',
    'pytest-bdd', 'Behave', 'Cucumber', 'SpecFlow',
    'Pact', 'WireMock', 'MSW',

    # ── APIs & Protocols ──────────────────────────────────────────────────────
    'REST', 'GraphQL', 'gRPC', 'WebSocket', 'WebRTC', 'MQTT', 'AMQP',
    'HTTP/2', 'HTTP/3', 'SOAP', 'OpenAPI', 'Swagger', 'Postman',
    'Insomnia', 'tRPC', 'JSON-RPC', 'Server-Sent Events', 'Webhooks',
    'OAuth 2.0', 'OpenID Connect', 'LDAP',

    # ── Security ──────────────────────────────────────────────────────────────
    'OWASP', 'JWT', 'SAML', 'SSL/TLS', 'PKI', 'Penetration Testing',
    'Burp Suite', 'Metasploit', 'Nmap', 'Wireshark', 'Nessus',
    'Snyk', 'SonarQube', 'Zero Trust', 'SOC 2', 'GDPR', 'HIPAA',
    'PCI DSS', 'ISO 27001', 'CIS Benchmarks', 'CSPM', 'SAST', 'DAST',
    'Security Auditing', 'Threat Modeling',

    # ── Version Control ───────────────────────────────────────────────────────
    'Git', 'GitHub', 'GitLab', 'Bitbucket', 'SVN', 'Mercurial', 'Perforce',

    # ── Project Management & Methodologies ────────────────────────────────────
    'Agile', 'Scrum', 'Kanban', 'SAFe', 'Lean', 'Waterfall', 'PRINCE2',
    'Jira', 'Confluence', 'Notion', 'Linear', 'Trello', 'Asana',
    'Monday.com', 'ClickUp', 'Basecamp', 'OKRs', 'Shape Up',
    'Design Thinking', 'Lean Six Sigma', 'PMP',

    # ── Design / UX ───────────────────────────────────────────────────────────
    'Figma', 'Adobe XD', 'Sketch', 'InVision', 'Zeplin',
    'Adobe Photoshop', 'Adobe Illustrator', 'Adobe After Effects',
    'Framer', 'Miro', 'Canva', 'ProtoPie',
    'UX Research', 'Usability Testing', 'Information Architecture',
    'Accessibility', 'WCAG', 'Design Systems', 'User Interviews',
    'Wireframing', 'Prototyping', 'User Story Mapping',

    # ── CMS / E-commerce ──────────────────────────────────────────────────────
    'WordPress', 'Contentful', 'Strapi', 'Sanity', 'Ghost',
    'Drupal', 'Joomla', 'Prismic', 'Webflow',
    'Shopify', 'WooCommerce', 'Magento', 'BigCommerce', 'Medusa',

    # ── Blockchain / Web3 ─────────────────────────────────────────────────────
    'Ethereum', 'Bitcoin', 'Solana', 'Polygon', 'Chainlink', 'IPFS',
    'Web3.js', 'Ethers.js', 'Hardhat', 'Truffle', 'Foundry',
    'OpenZeppelin', 'Smart Contracts', 'DeFi', 'NFT',

    # ── Game Development ──────────────────────────────────────────────────────
    'Unity', 'Unreal Engine', 'Godot', 'Phaser', 'Pygame', 'MonoGame',
    'LibGDX', 'Cocos2d', 'GameMaker', 'SDL', 'Bevy',

    # ── Embedded / IoT ────────────────────────────────────────────────────────
    'FreeRTOS', 'Zephyr', 'Arduino', 'Raspberry Pi', 'ESP32', 'STM32',
    'CAN Bus', 'I2C', 'SPI', 'UART', 'Modbus', 'OPC-UA',
    'Bluetooth LE', 'Zigbee', 'LoRa', 'NB-IoT', 'JTAG',

    # ── Systems / Networking ──────────────────────────────────────────────────
    'Linux', 'Unix Administration', 'Windows Server', 'TCP/IP', 'DNS',
    'BGP', 'OSPF', 'VPN', 'Load Balancing', 'CDN', 'Firewall',
    'Active Directory', 'Kubernetes Networking', 'eBPF',
    'SD-WAN', 'VLAN', 'OpenStack',

    # ── AI / LLM Tooling ──────────────────────────────────────────────────────
    'Prompt Engineering', 'RAG', 'Fine-tuning', 'LoRA', 'QLoRA',
    'Function Calling', 'AI Agents', 'Vector Embeddings',
    'Semantic Search', 'LLM Evaluation', 'LangGraph', 'CrewAI',
    'AutoGen', 'Claude API', 'GPT API', 'Gemini API',

    # ── Communication & Interpersonal ─────────────────────────────────────────
    'Communication', 'Written Communication', 'Verbal Communication',
    'Active Listening', 'Public Speaking', 'Presentation Skills',
    'Storytelling', 'Technical Writing', 'Business Writing',
    'Negotiation', 'Persuasion', 'Conflict Resolution',
    'Cross-functional Collaboration', 'Stakeholder Management',
    'Client Relationship Management', 'Interpersonal Skills',

    # ── Leadership & Management ────────────────────────────────────────────────
    'Leadership', 'Team Leadership', 'People Management',
    'Mentoring', 'Coaching', 'Performance Management',
    'Talent Acquisition', 'Succession Planning', 'Delegation',
    'Decision Making', 'Strategic Planning', 'Vision Setting',
    'Change Management', 'Organisational Development',
    'Executive Presence', 'Crisis Management',

    # ── Problem Solving & Critical Thinking ───────────────────────────────────
    'Problem Solving', 'Critical Thinking', 'Analytical Thinking',
    'Systems Thinking', 'Root Cause Analysis', 'Data-Driven Decision Making',
    'Research Skills', 'Hypothesis Testing', 'Innovation',
    'Creative Thinking', 'First Principles Thinking',

    # ── Time Management & Productivity ────────────────────────────────────────
    'Time Management', 'Prioritisation', 'Goal Setting', 'Self-Management',
    'Attention to Detail', 'Multitasking', 'Adaptability', 'Resilience',
    'Stress Management', 'Remote Work', 'Async Communication',

    # ── Finance & Accounting ──────────────────────────────────────────────────
    'Financial Analysis', 'Financial Modelling', 'Budgeting', 'Forecasting',
    'Accounting', 'Bookkeeping', 'Accounts Payable', 'Accounts Receivable',
    'Payroll', 'Tax Compliance', 'Auditing', 'Internal Audit',
    'Cost Accounting', 'Management Accounting', 'GAAP', 'IFRS',
    'Excel', 'Microsoft Excel', 'QuickBooks', 'SAP FI', 'Oracle Financials',
    'NetSuite', 'Xero', 'FreshBooks', 'Sage',
    'Corporate Finance', 'Investment Analysis', 'Equity Research',
    'Valuation', 'Mergers & Acquisitions', 'Private Equity',
    'Portfolio Management', 'Risk Management', 'Treasury', 'Cash Flow Management',
    'Bloomberg Terminal', 'Capital IQ', 'Pitch Books',
    'CFA', 'CPA', 'ACCA', 'FRM',

    # ── Marketing & Growth ────────────────────────────────────────────────────
    'Digital Marketing', 'Content Marketing', 'Social Media Marketing',
    'Email Marketing', 'SEO', 'SEM', 'Pay-Per-Click (PPC)', 'Google Ads',
    'Facebook Ads', 'LinkedIn Ads', 'Influencer Marketing',
    'Brand Management', 'Brand Strategy', 'Product Marketing',
    'Growth Hacking', 'Demand Generation', 'Lead Generation',
    'Conversion Rate Optimisation', 'Landing Page Optimisation',
    'Marketing Automation', 'HubSpot', 'Marketo', 'Pardot', 'Mailchimp',
    'Klaviyo', 'Salesforce Marketing Cloud', 'ActiveCampaign',
    'Copywriting', 'Content Strategy', 'Editorial Calendar',
    'Public Relations', 'Media Relations', 'Press Releases',
    'Community Management', 'Affiliate Marketing', 'Partnership Marketing',
    'Event Marketing', 'Trade Show Management', 'Webinar Hosting',

    # ── Sales & Business Development ──────────────────────────────────────────
    'Sales', 'B2B Sales', 'B2C Sales', 'Enterprise Sales', 'SaaS Sales',
    'Consultative Selling', 'Solution Selling', 'Account Management',
    'Business Development', 'Channel Sales', 'Inside Sales', 'Field Sales',
    'Sales Strategy', 'Sales Forecasting', 'Pipeline Management',
    'Cold Calling', 'Cold Outreach', 'Objection Handling',
    'Salesforce CRM', 'HubSpot CRM', 'Pipedrive', 'Outreach', 'Gong',
    'Sales Navigator', 'ZoomInfo', 'Apollo.io',
    'RFP Management', 'Contract Negotiation', 'Proposal Writing',
    'Customer Success', 'Upselling', 'Cross-selling', 'Churn Reduction',

    # ── Operations & Supply Chain ──────────────────────────────────────────────
    'Operations Management', 'Process Improvement', 'Process Optimisation',
    'Business Process Management', 'Workflow Automation',
    'Supply Chain Management', 'Logistics', 'Procurement', 'Vendor Management',
    'Inventory Management', 'Demand Planning', 'Warehouse Management',
    'Shipping & Fulfilment', 'Last-Mile Delivery', 'ERP Systems',
    'SAP', 'SAP ERP', 'Oracle ERP', 'Microsoft Dynamics', 'NetSuite ERP',
    'Lean Manufacturing', 'Six Sigma', 'Kaizen', 'Total Quality Management',
    'ISO 9001', 'CAPA', 'Quality Assurance', 'Quality Control',

    # ── Human Resources ───────────────────────────────────────────────────────
    'Human Resources', 'HR Management', 'Recruitment', 'Talent Management',
    'Onboarding', 'Employee Engagement', 'Employee Relations',
    'Compensation & Benefits', 'Job Evaluation', 'HR Policies',
    'Labour Law', 'Workforce Planning', 'Organisational Design',
    'Learning & Development', 'Training Design', 'Instructional Design',
    'HR Analytics', 'HRIS', 'Workday', 'BambooHR', 'SAP SuccessFactors',
    'Greenhouse', 'Lever', 'Workable', 'LinkedIn Recruiter',
    'Diversity & Inclusion', 'DEI Strategy', 'Culture Building',

    # ── Customer Service & Support ────────────────────────────────────────────
    'Customer Service', 'Customer Support', 'Technical Support',
    'Help Desk', 'Service Desk', 'ITIL', 'SLA Management',
    'Zendesk', 'Freshdesk', 'Intercom', 'ServiceNow', 'Salesforce Service Cloud',
    'Live Chat', 'Ticket Management', 'Escalation Management',
    'Customer Satisfaction (CSAT)', 'Net Promoter Score (NPS)',
    'Voice of Customer', 'Customer Journey Mapping',

    # ── Legal ─────────────────────────────────────────────────────────────────
    'Legal Research', 'Legal Writing', 'Contract Drafting',
    'Contract Review', 'Corporate Law', 'Commercial Law',
    'Employment Law', 'Intellectual Property', 'Data Privacy',
    'Regulatory Compliance', 'Litigation', 'Arbitration', 'Mediation',
    'Due Diligence', 'Legal Operations', 'E-Discovery',

    # ── Healthcare ────────────────────────────────────────────────────────────
    'Patient Care', 'Clinical Documentation', 'Electronic Health Records (EHR)',
    'Epic Systems', 'Cerner', 'MEDITECH', 'HL7', 'FHIR',
    'Medical Coding', 'ICD-10', 'CPT Coding', 'Revenue Cycle Management',
    'Healthcare Compliance', 'HIPAA Compliance', 'Clinical Research',
    'Clinical Trials', 'Pharmacovigilance', 'Regulatory Affairs',
    'Nursing', 'Telemedicine', 'Health Informatics', 'Public Health',

    # ── Education & Training ──────────────────────────────────────────────────
    'Curriculum Development', 'Lesson Planning', 'Classroom Management',
    'eLearning', 'Learning Management Systems', 'Moodle', 'Canvas',
    'Blackboard', 'Articulate Storyline', 'Adobe Captivate',
    'Facilitation', 'Workshop Facilitation', 'Train the Trainer',
    'Assessment Design', 'Educational Technology',

    # ── Architecture & Engineering ────────────────────────────────────────────
    'System Architecture', 'Software Architecture', 'Solution Architecture',
    'Enterprise Architecture', 'Domain-Driven Design', 'Microservices',
    'Monolithic Architecture', 'Event-Driven Architecture',
    'TOGAF', 'ArchiMate', 'UML', 'C4 Model', 'ADR',
    'Civil Engineering', 'Structural Engineering', 'Mechanical Engineering',
    'Electrical Engineering', 'AutoCAD', 'SolidWorks', 'Revit', 'BIM',

    # ── Science & Research ────────────────────────────────────────────────────
    'Research', 'Quantitative Research', 'Qualitative Research',
    'Statistical Analysis', 'Experimental Design', 'Literature Review',
    'Academic Writing', 'Grant Writing', 'Peer Review',
    'Laboratory Skills', 'PCR', 'CRISPR', 'Cell Culture', 'Flow Cytometry',
    'Mass Spectrometry', 'NMR Spectroscopy', 'ELISA',
    'Bioinformatics', 'Genomics', 'Proteomics', 'Clinical Data Management',

    # ── Media, Journalism & Content ───────────────────────────────────────────
    'Journalism', 'Investigative Reporting', 'Fact-Checking', 'Editing',
    'Proofreading', 'Video Production', 'Video Editing', 'Podcast Production',
    'Adobe Premiere Pro', 'Final Cut Pro', 'DaVinci Resolve',
    'Adobe Audition', 'Photography', 'Photo Editing',
    'Adobe Lightroom', 'Social Media Content Creation', 'Scriptwriting',

    # ── General Business & Strategy ───────────────────────────────────────────
    'Business Strategy', 'Strategic Analysis', 'Market Research',
    'Competitive Analysis', 'Business Case Development', 'Go-to-Market Strategy',
    'Product Strategy', 'Product Roadmap', 'Product Management',
    'Product Discovery', 'User Story Writing', 'Backlog Grooming',
    'Sprint Planning', 'Stakeholder Presentations', 'Executive Reporting',
    'Consulting', 'Management Consulting', 'Business Analysis',
    'Requirements Gathering', 'Gap Analysis', 'Business Intelligence',
    'Microsoft Office', 'Microsoft Word', 'Microsoft PowerPoint',
    'Microsoft Teams', 'Google Workspace', 'Google Docs', 'Google Sheets',
    'Slack', 'Zoom',
]
# fmt: on


def upgrade() -> None:
    conn = op.get_bind()
    for name in _SKILLS:
        conn.execute(
            sa.text(
                "INSERT INTO skills (name, label, created_at, updated_at) "
                "VALUES (:name, :label, NOW(), NOW()) "
                "ON CONFLICT (name) DO NOTHING"
            ),
            {'name': name, 'label': name},
        )


def downgrade() -> None:
    conn = op.get_bind()
    for name in _SKILLS:
        conn.execute(
            sa.text("DELETE FROM skills WHERE name = :name"),
            {'name': name},
        )

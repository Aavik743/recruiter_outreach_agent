import re

from models import Job


TECHNICAL_SKILLS = frozenset({
    # Programming languages
    'python', 'java', 'javascript', 'typescript', 'golang', 'rust',
    'ruby', 'php', 'swift', 'kotlin', 'scala', 'sql', 'html', 'css',
    'c++', 'c#', '.net', 'r',
    # Frameworks
    'django', 'flask', 'fastapi', 'react', 'angular', 'vue',
    'express', 'spring', 'rails', 'nextjs', 'node.js',
    # Data / ML
    'pandas', 'numpy', 'tensorflow', 'pytorch', 'keras',
    'spark', 'hadoop', 'airflow', 'kafka', 'dbt',
    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
    'dynamodb', 'cassandra', 'sqlite',
    # Cloud / Infra
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform',
    'jenkins', 'ansible', 'gitlab', 'github', 'ci/cd',
    # Practices
    'agile', 'scrum', 'rest', 'graphql', 'microservices',
    'devops', 'linux', 'nginx',
    # Testing
    'pytest', 'junit', 'selenium', 'cypress',
})

STOP_WORDS = frozenset({
    'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
    'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are',
    'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does',
    'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can',
    'shall', 'not', 'this', 'that', 'these', 'those', 'you', 'he',
    'she', 'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'when',
    'where', 'why', 'how', 'all', 'each', 'every', 'both', 'few',
    'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'only',
    'own', 'same', 'so', 'than', 'too', 'very', 'just', 'about',
    'above', 'after', 'again', 'also', 'any', 'because', 'before',
    'between', 'during', 'if', 'into', 'its', 'our', 'out', 'over',
    'their', 'then', 'there', 'through', 'under', 'up', 'your',
    'must', 'able', 'well', 'work', 'working', 'experience', 'years',
    'year', 'team', 'including', 'using', 'ability', 'strong',
    'knowledge', 'looking', 'join', 'role', 'position',
    'responsibilities', 'requirements', 'qualifications', 'benefits',
    'salary', 'apply', 'please', 'required', 'preferred', 'skills',
    'opportunity', 'company', 'job', 'ideal', 'candidate', 'etc',
    'per', 'will', 'new', 'like', 'based', 'related', 'within',
})

_TOKEN_RE = re.compile(r'[a-z0-9#+./-]+')

_TITLE_PORTION = 0.35
_SKILL_PORTION = 0.45
_GENERAL_PORTION = 0.20


def score_job(job: Job, master_resume: str) -> int:
    resume_tokens = _tokenize(master_resume)
    title_tokens = _tokenize(job.title) - STOP_WORDS
    desc_tokens = _tokenize(job.description) - STOP_WORDS

    if not desc_tokens:
        return 0

    title_kw: set[str] = set()
    skill_kw: set[str] = set()
    general_kw: set[str] = set()

    for token in desc_tokens:
        if token in title_tokens:
            title_kw.add(token)
        elif token in TECHNICAL_SKILLS:
            skill_kw.add(token)
        else:
            general_kw.add(token)

    title_ratio = _match_ratio(title_kw, resume_tokens)
    skill_ratio = _match_ratio(skill_kw, resume_tokens)
    general_ratio = _match_ratio(general_kw, resume_tokens)

    raw_weights = {
        'title': _TITLE_PORTION if title_kw else 0.0,
        'skill': _SKILL_PORTION if skill_kw else 0.0,
        'general': _GENERAL_PORTION if general_kw else 0.0,
    }
    total = sum(raw_weights.values())
    if total == 0.0:
        return 0

    score = (
        title_ratio * raw_weights['title']
        + skill_ratio * raw_weights['skill']
        + general_ratio * raw_weights['general']
    ) / total * 100

    return min(100, round(score))


def _tokenize(text: str) -> set[str]:
    tokens = _TOKEN_RE.findall(text.lower())
    return {t for t in tokens if len(t) >= 2}


def _match_ratio(keywords: set[str], reference: set[str]) -> float:
    if not keywords:
        return 0.0
    return len(keywords & reference) / len(keywords)

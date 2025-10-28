# backend/src/data_preprocessing.py
import re
import unicodedata
import pandas as pd

# Text normalization for Vietnamese and mixed-language fields
def normalize_text(text):
    if pd.isna(text):
        return ''
    if not isinstance(text, str):
        text = str(text)
    # normalize unicode
    text = unicodedata.normalize('NFC', text)
    # remove HTML tags
    text = re.sub(r'<[^>]+>', ' ', text)
    # unify whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove bullet symbols / formatting artifacts
    text = re.sub(r"[•●▪·\-–—]+", " ", text)
    # fix common prefixes like 'Mô tả công việc:'
    text = re.sub(r'(?i)mo\s?tả\s+công\s+việc:?', ' ', text)
    text = re.sub(r'(?i)yeu\s+cau:?', ' ', text)
    text = re.sub(r'(?i)\bï»¿\b', '', text)
    # Remove repeated punctuations and newlines
    text = re.sub(r"(\s*\n\s*)+", " ", text)
    text = re.sub(r"[ ]{2,}", " ", text)

    # Remove repeated boilerplate labels
    text = re.sub(
        r"(m[oô] t[aả] c[oô]ng vi[eệ]c|y[eê]u c[aà]u [uư]ng vi[eệ]n|quy[eê]n l[oơ]i|th[oô]ng tin th[eê]m):?",
        " ",
        text, flags=re.I
    )

    return text

# Salary parsing: handle VND, USD, ranges, words like 'thương lượng'
CURRENCY_PATTERNS = {
    'vnd': re.compile(r'(?i)\bvnd\b|\bvnđ\b|đ|₫'),
    'usd': re.compile(r'(?i)usd|\$')
}

def parse_salary_field(s):
    """Return (min, max, unit) where unit is 'vnd' or 'usd' or None. If missing, return (None,None,None)."""
    if pd.isna(s):
        return (None, None, None)
    s = str(s)
    s = s.replace(',', '.')  # some datasets use '.' as thousand sep or decimal
    s = s.replace('–', '-')
    # extract numbers
    nums = re.findall(r'\d+[\.,]?\d*', s)
    unit = None
    if re.search(r'(?i)usd|\$', s):
        unit = 'usd'
    elif re.search(r'(?i)vnd|vnđ|triệu|triệu|triệu|đồng|d', s):
        unit = 'vnd'

    if not nums:
        return (None, None, unit)

    # convert to float
    nums_f = []
    for n in nums:
        try:
            nums_f.append(float(n))
        except:
            try:
                nums_f.append(float(n.replace('.', '')))
            except:
                pass
    if not nums_f:
        return (None, None, unit)

    if len(nums_f) == 1:
        return (nums_f[0], nums_f[0], unit)
    else:
        return (nums_f[0], nums_f[-1], unit)

def normalize_salary_to_vnd(s_min, s_max, unit):
    if s_min is None and s_max is None:
        return (None, None)
    if unit is None:
        # assume vnd and unit is in millions if typical values small (e.g., <1000)
        unit = 'vnd'
    if unit == 'usd':
        # set conversion rate (adjustable)
        USD_TO_VND = 25000
        return (s_min * USD_TO_VND if s_min else None, s_max * USD_TO_VND if s_max else None)
    elif unit == 'vnd':
        # if s_min seems like 'triệu' (i.e., typical 10-50), interpret as million VND
        def fix_val(v):
            if v is None:
                return None
            if v < 1000:  # treat as million
                return v * 1_000_000
            else:
                return v
        return (fix_val(s_min), fix_val(s_max))
    else:
        return (s_min, s_max)

# Experience parsing: extract years
def parse_experience(exp):
    if pd.isna(exp):
        return None
    s = str(exp)
    nums = re.findall(r'\d+', s)
    if not nums:
        # look for words like 'Senior' -> infer level
        if re.search(r'(?i)senior|lead|manager', s):
            return 5
        if re.search(r'(?i)junior|intern|student|thực tập', s):
            return 0
        return None
    # No experience
    if re.search(r"kh[oô]ng y[eê]u c[aà]u|no experience", s):
        return 0

    # Range
    m = re.search(r"(\d+)\s*-\s*(\d+)", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2

    # "Tren X nam"
    m = re.search(r"tr[eê]n\s*(\d+)", s)
    if m:
        return int(m.group(1)) + 1

    # "Duoi X nam"
    m = re.search(r"d[uư][oơ]i\s*(\d+)", s)
    if m:
        return 0

    # Single number
    m = re.search(r"(\d+)", s)
    if m:
        return int(m.group(1))
    # take first numeric as years
    try:
        return int(nums[0])
    except:
        return None

# Education mapping
EDU_MAP = {
    "trung cấp": 1,
    "cao đẳng": 1,
    "đại học": 2,
    "đại học trở lên": 2,
    "cử nhân": 2,
    "cao học": 3,
    "thạc sĩ": 3,
    "tiến sĩ": 4,
    "master": 3,
    "bachelor": 2,
    "phd": 4,
    "none": 0,
    "not required": 0,
    "không yêu cầu": 0,
}

def map_education(e):
    if pd.isna(e):
        return None
    s = str(e).lower()
    for k,v in EDU_MAP.items():
        if k in s:
            return v
    return None

# Location normalization
LOCATION_ALIASES = {
    'hcm': ['hồ chí minh', 'tp.hcm', 'tphcm', 'ho chi minh city', 'hcmc', 'hcm'],
    'hn': ['hà nội', 'ha noi', 'hn']
}

def normalize_location(loc):
    if pd.isna(loc):
        return None
    s = str(loc).lower()
    s = re.sub(r'\s+', ' ', s).strip()
    for k,alts in LOCATION_ALIASES.items():
        for a in alts:
            if a in s:
                return k
    return s

# Skill extraction: simple keyword extraction using regex
def extract_skills(text):
    if not text:
        return []
    # naive: split by commas, semicolons, newlines, or 'và' / 'and'
    parts = re.split(r'[;,\n\|/]|\bvà\b|\band\b', text)
    skills = [p.strip() for p in parts if 2 <= len(p.strip()) <= 80]
    # further split multi-skills in parts separated by spaces if they contain '/'
    return list(dict.fromkeys([s for s in skills if s]))

# Load CSV safely (copied from notebook)
def load_csv_safe(path):
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Failed to read {path}: {e}")
        return None

def clean_jobs_df(df, source_name='df'):
    df = df.copy()
    # normalize column names
    df.columns = [c.strip() for c in df.columns]

    # common mappings (best effort)
    colmap = {}
    # detect similar names
    lowcols = {c.lower(): c for c in df.columns}
    def find_col(possible):
        for p in possible:
            if p.lower() in lowcols:
                return lowcols[p.lower()]
        return None

    colmap['job_title'] = find_col(['Job', 'job', 'job_title', 'job title', 'jobTitle'])
    colmap['description'] = find_col(['Description', 'description', 'Mô tả', 'Mo ta'])
    colmap['requirement'] = find_col(['Requirement', 'requirement', 'Yêu cầu', 'Yeu cau', 'Requirement'])
    colmap['benefit'] = find_col(['Benefit', 'benefit', 'Quyền lợi', 'Benefit'])
    colmap['salary'] = find_col(['Salary', 'salary', 'Salary_range', 'SalaryRange'])
    colmap['salary_min'] = find_col(['salary_min', 'Salary_min'])
    colmap['salary_max'] = find_col(['salary_max', 'Salary_max'])
    colmap['unit'] = find_col(['unit', 'currency'])
    colmap['experience'] = find_col(['Experience', 'experience', 'Kinh nghiệm', 'Exp'])
    colmap['education'] = find_col(['Education', 'education', 'Yêu cầu học vấn'])
    colmap['skills'] = find_col(['skills', 'Skill', 'skill', 'Keyword', 'keywords'])
    colmap['location'] = find_col(['Location', 'location', 'City', 'city'])
    colmap['company'] = find_col(['Company', 'company', 'Employer'])
    colmap['industry'] = find_col(['Industry', 'industry', 'job_fields'])
    colmap['position_level'] = find_col(['Position', 'position', 'position_level', 'level'])

    # Create unified columns
    for k,v in colmap.items():
        df[k] = df[v] if v in df.columns else None

    # Normalize text fields
    for tcol in ['job_title', 'description', 'requirement', 'benefit', 'skills', 'company', 'industry']:
        if tcol in df.columns:
            df[tcol] = df[tcol].apply(normalize_text)

    # Parse salary
    def compute_salary(row):
        # priority: salary_min & salary_max & unit columns if present
        smin = row.get('salary_min')
        smax = row.get('salary_max')
        unit = row.get('unit')
        if pd.notna(smin) or pd.notna(smax):
            try:
                sminf = float(smin) if pd.notna(smin) else None
            except:
                sminf = None
            try:
                smaxf = float(smax) if pd.notna(smax) else None
            except:
                smaxf = None
            mins, maxs = normalize_salary_to_vnd(sminf, smaxf, str(unit).lower() if pd.notna(unit) else None)
            return pd.Series({'salary_min_vnd': mins, 'salary_max_vnd': maxs})
        # else try to parse from 'salary' column
        s = row.get('salary')
        if pd.isna(s):
            return pd.Series({'salary_min_vnd': None, 'salary_max_vnd': None})
        pmin, pmax, unit = parse_salary_field(s)
        mins, maxs = normalize_salary_to_vnd(pmin, pmax, unit)
        return pd.Series({'salary_min_vnd': mins, 'salary_max_vnd': maxs})

    sal = df.apply(compute_salary, axis=1)
    df['salary_min_vnd'] = sal['salary_min_vnd']
    df['salary_max_vnd'] = sal['salary_max_vnd']

    # Experience
    df['experience_years'] = df['experience'].apply(parse_experience)

    # Education
    df['education_level'] = df['education'].apply(map_education)

    # Location
    df['location_norm'] = df['location'].apply(normalize_location)

    # Extract skill lists
    df['skills_list'] = df['skills'].apply(extract_skills)

    # Derive salary_mean
    def mean_salary(r):
        a = r['salary_min_vnd']
        b = r['salary_max_vnd']
        if pd.notna(a) and pd.notna(b):
            return (a + b) / 2
        if pd.notna(a):
            return a
        if pd.notna(b):
            return b
        return None
    df['salary_mean_vnd'] = df.apply(mean_salary, axis=1)

    # Keep only relevant columns in a canonical order
    keep_cols = ['job_title','company','description','requirement','benefit','skills','skills_list',
                 'salary_min_vnd','salary_max_vnd','salary_mean_vnd','experience_years','education_level',
                 'location_norm','industry','position_level','job_type']
    for c in keep_cols:
        if c not in df.columns:
            df[c] = None

    return df[keep_cols]

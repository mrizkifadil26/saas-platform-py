import hashlib


def _seed(s: str) -> int:
    # stable across runs
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def dummy_company(domain: str) -> dict:
    n = _seed(domain)
    industries = ["Software", "FinTech", "E-commerce", "Healthcare", "Manufacturing"]
    return {
        "id": f"cmp_{n:08x}",
        "name": domain.split(".")[0].capitalize() + " Inc",
        "domain": domain,
        "industry": industries[n % len(industries)],
        "employee_count": 10 + (n % 5000),
    }


def dummy_person(domain: str, email_hint: str | None = None) -> dict:
    n = _seed((domain or "") + "|" + (email_hint or ""))
    first = ["Ari", "Bima", "Citra", "Dewi", "Eka", "Fajar", "Gita", "Hadi"]
    last = ["Putra", "Sari", "Wijaya", "Pratama", "Utami", "Nugroho"]
    titles = ["Engineer", "Manager", "Analyst", "Director", "Founder", "Sales Lead"]
    fn = first[n % len(first)]
    ln = last[(n // 7) % len(last)]
    title = titles[(n // 13) % len(titles)]
    email = None
    if email_hint:
        email = email_hint
    return {
        "id": f"ppl_{n:08x}",
        "full_name": f"{fn} {ln}",
        "title": title,
        "email": email,
        "company_domain": domain,
    }

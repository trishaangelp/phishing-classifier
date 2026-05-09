import re
import urllib.parse
import tldextract

SUSPICIOUS_TLDS = {
    "xyz", "tk", "ml", "ga", "cf", "gq", "pw", "top", "club",
    "work", "click", "link", "online", "site", "tech", "live",
}

SHORTENER_DOMAINS = {
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
    "is.gd", "buff.ly", "adf.ly", "short.link", "rebrand.ly",
}

BRAND_KEYWORDS = [
    "paypal", "apple", "google", "amazon", "facebook", "microsoft",
    "netflix", "instagram", "twitter", "linkedin", "dropbox",
    "bankofamerica", "chase", "wellsfargo", "citibank", "dhl",
    "fedex", "usps", "ups", "ebay", "walmart", "yahoo",
]


def extract_features(url: str) -> dict:
    """
    Extract 15 numerical features from a URL string.
    Returns a dict that can be passed directly to the model.
    """
    url = url.strip()

    try:
        parsed = urllib.parse.urlparse(url)
    except Exception:
        parsed = urllib.parse.urlparse("")

    extracted = tldextract.extract(url)
    domain = extracted.domain.lower()
    suffix = extracted.suffix.lower()
    subdomain = extracted.subdomain.lower()
    full_domain = f"{extracted.domain}.{extracted.suffix}".lower()
    path = parsed.path or ""
    query = parsed.query or ""

    # 1. URL total length
    url_length = len(url)

    # 2. Domain length
    domain_length = len(full_domain)

    # 3. Number of dots in full URL
    num_dots = url.count(".")

    # 4. Number of hyphens in domain
    num_hyphens = domain.count("-")

    # 5. Number of subdomains
    num_subdomains = len(subdomain.split(".")) if subdomain else 0

    # 6. Has IP address instead of domain name
    ip_pattern = re.compile(
        r"^(\d{1,3}\.){3}\d{1,3}$"
    )
    has_ip = int(bool(ip_pattern.match(extracted.domain)))

    # 7. Has @ symbol in URL (common phishing trick)
    has_at = int("@" in url)

    # 8. Uses HTTPS
    has_https = int(parsed.scheme == "https")

    # 9. Is a URL shortener
    is_shortener = int(full_domain in SHORTENER_DOMAINS)

    # 10. Suspicious TLD
    suspicious_tld = int(suffix in SUSPICIOUS_TLDS)

    # 11. Brand keyword in domain or subdomain (typosquatting indicator)
    combined = f"{subdomain} {domain}"
    has_brand_keyword = int(
        any(brand in combined for brand in BRAND_KEYWORDS)
    )

    # 12. Path depth (number of slashes in path)
    path_depth = len([p for p in path.split("/") if p])

    # 13. Has query string
    has_query = int(bool(query))

    # 14. Number of special characters (%, =, &) in URL
    num_special_chars = sum(url.count(c) for c in ["%", "=", "&", "?"])

    # 15. Double slash in path (redirect trick)
    has_double_slash = int("//" in path)

    return {
        "url_length": url_length,
        "domain_length": domain_length,
        "num_dots": num_dots,
        "num_hyphens": num_hyphens,
        "num_subdomains": num_subdomains,
        "has_ip": has_ip,
        "has_at": has_at,
        "has_https": has_https,
        "is_shortener": is_shortener,
        "suspicious_tld": suspicious_tld,
        "has_brand_keyword": has_brand_keyword,
        "path_depth": path_depth,
        "has_query": has_query,
        "num_special_chars": num_special_chars,
        "has_double_slash": has_double_slash,
    }


FEATURE_NAMES = list(extract_features("http://example.com").keys())

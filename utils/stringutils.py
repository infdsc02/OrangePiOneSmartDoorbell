def ip_from_url(url: str):
    return url.split("://")[1].split(":")[0]


def is_empty_string(val):
    if val is None:
        return True
    return len(val.strip()) == 0

import hashlib

hwid = "D11B-4863-A1D5"
MASTER_SECRET = "JUVIKS_2026_HERO_SECURE_VAULT"

def gerar_chave_final(hwid):
    raw_key = hashlib.sha256(f"{hwid}{MASTER_SECRET}".encode()).hexdigest().upper()[:16]
    return f"{raw_key[:4]}-{raw_key[4:8]}-{raw_key[8:12]}-{raw_key[12:]}"

print(gerar_chave_final(hwid))

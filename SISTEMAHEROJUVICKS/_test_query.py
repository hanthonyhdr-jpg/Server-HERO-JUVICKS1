import sys
sys.path.insert(0, 'PY')
from database import buscar_dados, inicializar_banco

inicializar_banco()

# Teste 1: Query com LIKE e % sem parâmetros (o caso que dava erro)
df = buscar_dados("SELECT id FROM clientes WHERE id LIKE 'CLI-%'")
print("Teste 1 (LIKE sem params):", len(df), "resultados")

# Teste 2: Query com LIKE e parâmetros
df2 = buscar_dados("SELECT id FROM clientes WHERE id LIKE ?", ("CLI-%",))
print("Teste 2 (LIKE com params):", len(df2), "resultados")

# Teste 3: Query simples
df3 = buscar_dados("SELECT COUNT(*) FROM chaves_acesso WHERE status=1")
print("Teste 3 (COUNT):", df3.iloc[0,0])

print("\n=== TODOS OS TESTES OK ===")

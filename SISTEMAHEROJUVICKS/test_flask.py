import socket
import time
import requests
import threading

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def test_flask():
    print("=== TESTE FLASK ===")
    
    # Testar portas
    for port in [5000, 5001]:
        if check_port(port):
            print(f"✓ Porta {port} ABERTA")
        else:
            print(f"✗ Porta {port} FECHADA")
    
    # Testar Ngrok
    try:
        r = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=2)
        if r.status_code == 200:
            tunnels = r.json().get('tunnels', [])
            print(f"✓ Ngrok ativo: {len(tunnels)} tunnels")
            for t in tunnels:
                print(f"  - {t.get('public_url')}")
        else:
            print("✗ Ngrok sem resposta")
    except Exception as e:
        print(f"✗ Ngrok offline: {e}")
    
    # Testar API
    for port in [5000, 5001]:
        try:
            r = requests.get(f"http://localhost:{port}/", timeout=2)
            print(f"✓ API responde na porta {port}")
        except Exception as e:
            print(f"✗ API não responde na porta {port}: {e}")
    
    print("=== FIM TESTE ===")

if __name__ == "__main__":
    test_flask()
    input("Pressione Enter para sair...")
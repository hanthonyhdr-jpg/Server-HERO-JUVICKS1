import os
import shutil
import json
import time
import sys
from datetime import datetime, timedelta

# =====================================================================
# RENOVA SYSTEM - BACKUP AUTOMATICO v1.0
# Roda em segundo plano e salva o banco com data/hora no nome do arquivo
# =====================================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "sistema_vendas.db")
CONFIG_PATH = os.path.join(BASE_DIR, "backup_config.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
LOG_PATH = os.path.join(BASE_DIR, "backup_log.txt")

def log(msg):
    """Grava um log com data/hora no arquivo de log."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    linha = f"[{agora}] {msg}"
    print(linha)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(linha + "\n")

def carregar_config():
    """Lê as configurações do arquivo JSON."""
    config_padrao = {
        "frequencia": "diario",   # diario, semanal, mensal
        "hora": "02:00",          # Hora do backup (HH:MM) formato 24h
        "dia_semana": 1,          # 0=Segunda ... 6=Domingo (para semanal)
        "dia_mes": 1,             # Dia do mês (para mensal)
        "manter_ultimos": 30,     # Quantos backups manter (0 = manter todos)
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8", errors="replace") as f:
                cfg = json.load(f)
                # Preenche com padrão se alguma chave faltar
                for k, v in config_padrao.items():
                    if k not in cfg:
                        cfg[k] = v
                return cfg
        except Exception as e:
            log(f"ERRO ao ler config: {e}. Usando configuracao padrao.")
    return config_padrao

def fazer_backup():
    """Copia o banco de dados com nome contendo data e hora."""
    if not os.path.exists(DB_PATH):
        log("AVISO: Banco de dados nao encontrado. Backup ignorado.")
        return

    os.makedirs(BACKUP_DIR, exist_ok=True)

    agora = datetime.now()
    nome_arquivo = f"backup_{agora.strftime('%Y-%m-%d_%H-%M-%S')}.db"
    destino = os.path.join(BACKUP_DIR, nome_arquivo)

    try:
        shutil.copy2(DB_PATH, destino)
        tamanho = os.path.getsize(destino) / 1024
        log(f"BACKUP OK -> '{nome_arquivo}' ({tamanho:.1f} KB)")
        limpar_backups_antigos()
    except Exception as e:
        log(f"ERRO ao fazer backup: {e}")

def limpar_backups_antigos():
    """Remove backups mais antigos que o limite configurado."""
    cfg = carregar_config()
    limite = cfg.get("manter_ultimos", 30)
    if limite == 0:
        return  # Manter todos

    arquivos = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith("backup_") and f.endswith(".db")],
        reverse=True  # Mais recentes primeiro
    )

    if len(arquivos) > limite:
        para_remover = arquivos[limite:]
        for arq in para_remover:
            os.remove(os.path.join(BACKUP_DIR, arq))
            log(f"Backup antigo removido: {arq}")

def calcular_proximo_backup(cfg):
    """Calcula quando será o próximo backup com base na configuração."""
    agora = datetime.now()
    hora_str = cfg.get("hora", "02:00")
    hora, minuto = map(int, hora_str.split(":"))
    frequencia = cfg.get("frequencia", "diario")

    # Monta o horário alvo de hoje
    alvo = agora.replace(hour=hora, minute=minuto, second=0, microsecond=0)

    if frequencia == "diario":
        if alvo <= agora:
            alvo += timedelta(days=1)

    elif frequencia == "semanal":
        dia_semana_alvo = cfg.get("dia_semana", 1)  # 0=Segunda
        dias_ate = (dia_semana_alvo - agora.weekday()) % 7
        if dias_ate == 0 and alvo <= agora:
            dias_ate = 7
        alvo = (agora + timedelta(days=dias_ate)).replace(hour=hora, minute=minuto, second=0, microsecond=0)

    elif frequencia == "mensal":
        dia_mes_alvo = cfg.get("dia_mes", 1)
        alvo = alvo.replace(day=dia_mes_alvo)
        if alvo <= agora:
            # Avança para o mês seguinte
            if alvo.month == 12:
                alvo = alvo.replace(year=alvo.year + 1, month=1)
            else:
                alvo = alvo.replace(month=alvo.month + 1)

    return alvo

def main():
    log("=" * 55)
    log("JUVIKS07 BACKUP AUTO INICIADO")
    log("=" * 55)

    while True:
        cfg = carregar_config()
        proximo = calcular_proximo_backup(cfg)
        espera = (proximo - datetime.now()).total_seconds()

        frequencia = cfg.get("frequencia", "diario")
        hora = cfg.get("hora", "02:00")
        log(f"Proximo backup [{frequencia.upper()}] agendado para: {proximo.strftime('%d/%m/%Y as %H:%M')}")

        # Aguarda até o horário do backup (verificando a cada 60s para recarregar config)
        while datetime.now() < proximo:
            time.sleep(30)
            # Recarrega a config em loop para pegar mudanças em tempo real
            cfg_nova = carregar_config()
            if cfg_nova != cfg:
                log("Configuracao alterada! Recalculando proximo backup...")
                cfg = cfg_nova
                proximo = calcular_proximo_backup(cfg)

        fazer_backup()

if __name__ == "__main__":
    main()

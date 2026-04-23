# Robô de vagas executivas - Multi-sites
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time
import urllib.parse

# ===== CONFIGURAÇÕES (VOCÊ MUDA AQUI) =====
SEU_EMAIL = "paiva.consult@gmail.com"  # ← seu e-mail
SUA_SENHA_APP = "ydpc qbvu pxtc uzlt"  # ← senha do app Gmail
EMAIL_DESTINO = "paiva.consult@gmail.com"  # ← onde receber as vagas

# Cargos executivos que você quer
PALAVRAS_CHAVE = [
    "Enterprise Agile Coach",
    "Consultor de Transformação Organizacional",
    "Head de Delivery Transformation",
    "Lean Portfolio Execution Lead",
    "PMO Estratégico",
    "Transformation PMO",
    "Strategic Delivery Manager"
]

# Lista de sites para buscar (todos gratuitos)
SITES_BUSCA = [
    {
        "nome": "LinkedIn",
        "url": "https://www.linkedin.com/jobs/search/?keywords={palavra}&location=Brasil",
        "funciona": True
    },
    {
        "nome": "Indeed",
        "url": "https://br.indeed.com/jobs?q={palavra}&l=Brasil",
        "funciona": True
    },
    {
        "nome": "InfoJobs",
        "url": "https://www.infojobs.com.br/empregos.aspx?palabra={palavra}",
        "funciona": True
    },
    {
        "nome": "Curriculum",
        "url": "https://www.curriculum.com.br/vagas/{palavra}",
        "funciona": True
    },
    {
        "nome": "Gupy",
        "url": "https://portal.gupy.io/job-search/term={palavra}",
        "funciona": True
    },
    {
        "nome": "Solides",
        "url": "https://vagas.solides.com.br/vagas/todos/{palavra}",
        "funciona": True
    },
    {
        "nome": "Jobijoba",
        "url": "https://www.jobijoba.com.br/query/?what={palavra}",
        "funciona": True
    },
    {
        "nome": "Nerdin",
        "url": "https://nerdin.com.br/vagas.php?busca_vaga={palavra}",
        "funciona": True
    }
]

# ===== FUNÇÃO PRINCIPAL DE BUSCA =====
def buscar_todas_vagas():
    """Busca vagas em todos os sites e gera links diretos"""
    todas_vagas = []
    
    print(f"🔍 Buscando vagas em {len(SITES_BUSCA)} sites...")
    
    for cargo in PALAVRAS_CHAVE:
        print(f"\n📌 Buscando: {cargo}")
        
        for site in SITES_BUSCA:
            if not site["funciona"]:
                continue
                
            # Cria a URL de busca
            palavra_formatada = urllib.parse.quote(cargo)
            url_busca = site["url"].replace("{palavra}", palavra_formatada)
            
            # Adiciona a vaga (com link direto para busca)
            todas_vagas.append({
                "titulo": cargo,
                "site": site["nome"],
                "link": url_busca,
                "data": datetime.now().strftime("%Y-%m-%d")
            })
            print(f"  ✅ {site['nome']}: link gerado")
            
            time.sleep(0.5)  # pausa pequena
    
    return todas_vagas

def buscar_gupy_especifico():
    """Busca específica no Gupy (funciona melhor)"""
    vagas_gupy = []
    
    # URL da Gupy para busca (funciona!)
    base_url = "https://portal.gupy.io/jobs?term="
    
    for cargo in PALAVRAS_CHAVE:
        url = base_url + urllib.parse.quote(cargo)
        vagas_gupy.append({
            "titulo": f"🔍 {cargo} (Gupy - clique para buscar)",
            "site": "Gupy",
            "link": url,
            "data": datetime.now().strftime("%Y-%m-%d")
        })
    
    return vagas_gupy

def buscar_linkedin_filtrado():
    """Busca no LinkedIn com filtro de cargo exato"""
    vagas_linkedin = []
    
    for cargo in PALAVRAS_CHAVE:
        # LinkedIn com filtro de título exato
        url = f"https://www.linkedin.com/jobs/search/?keywords={urllib.parse.quote(cargo)}&location=Brasil&f_JT=FULL_TIME"
        vagas_linkedin.append({
            "titulo": f"🎯 {cargo} (LinkedIn - Filtrado)",
            "site": "LinkedIn",
            "link": url,
            "data": datetime.now().strftime("%Y-%m-%d")
        })
    
    return vagas_linkedin

def formatar_email(vagas):
    """Formata o e-mail de forma organizada"""
    if not vagas:
        return "Nenhuma vaga encontrada hoje."
    
    # Agrupa por site
    por_site = {}
    for vaga in vagas:
        site = vaga['site']
        if site not in por_site:
            por_site[site] = []
        por_site[site].append(vaga)
    
    corpo = f"""
🎯 VAGAS EXECUTIVAS - {datetime.now().strftime('%d/%m/%Y')}
Olá! Seu robô preparou uma busca personalizada para você.

📊 RESUMO: {len(vagas)} links gerados em {len(por_site)} sites diferentes

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"""
    
    for site, vagas_site in por_site.items():
        corpo += f"\n📌 {site.upper()}\n{'-' * 40}\n"
        for vaga in vagas_site[:5]:  # máximo 5 por site
            corpo += f"├─ {vaga['titulo']}\n"
            corpo += f"└─ 🔗 {vaga['link']}\n\n"
    
    corpo += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 DICAS IMPORTANTES:
• Cada link é uma busca PRONTA no site
• Basta CLICAR e filtrar os resultados
• Salve este e-mail e use todos os dias

🚀 BOA SORTE NAS CANDIDATURAS!

Seu robô de vagas executivas 🤖
"""
    
    return corpo

def enviar_email(vagas):
    """Envia o e-mail com todas as vagas"""
    if not vagas:
        print("⚠️ Nenhuma vaga encontrada")
        return
    
    corpo_email = formatar_email(vagas)
    
    msg = MIMEText(corpo_email, 'plain', 'utf-8')
    msg['Subject'] = f"🎯 {len(vagas)} links de vagas executivas - {datetime.now().strftime('%d/%m')}"
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SUA_SENHA_APP)
        server.send_message(msg)
        server.quit()
        print(f"📧 E-mail enviado com {len(vagas)} links para {EMAIL_DESTINO}")
    except Exception as erro:
        print(f"❌ Erro: {erro}")

def main():
    print("🚀 ROBÔ DE VAGAS EXECUTIVAS - MULTI SITES")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"🔎 Buscando: {len(PALAVRAS_CHAVE)} cargos em {len(SITES_BUSCA)} sites\n")
    
    # Busca todas as vagas
    todas_vagas = []
    
    # 1. Busca em todos os sites
    todas_vagas.extend(buscar_todas_vagas())
    
    # 2. Busca especial no Gupy
    todas_vagas.extend(buscar_gupy_especifico())
    
    # 3. Busca especial no LinkedIn
    todas_vagas.extend(buscar_linkedin_filtrado())
    
    # Remove duplicados (mesmo cargo + mesmo site)
    unicos = {}
    for v in todas_vagas:
        chave = f"{v['titulo']}_{v['site']}"
        if chave not in unicos:
            unicos[chave] = v
    
    vagas_final = list(unicos.values())
    
    print(f"\n✅ Total de {len(vagas_final)} links gerados")
    
    # Envia o e-mail
    enviar_email(vagas_final)
    
    print("🏁 Robô finalizado com sucesso!")

if __name__ == "__main__":
    main()

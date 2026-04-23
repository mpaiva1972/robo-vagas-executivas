# Robô de vagas executivas - versão para leigos
import requests
import json
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import time

# SUAS INFORMAÇÕES (você vai preencher depois)
SEU_EMAIL = "paiva.consult@gmail.com"  # ← MUDE AQUI
SUA_SENHA_APP = "ydpc qbvu pxtc uzlt"  # ← vamos criar mais tarde
EMAIL_DESTINO = "paiva.consult@gmail.com"  # ← para onde enviar as vagas

# Palavras-chave das vagas que você quer
PALAVRAS_CHAVE = [
    "Enterprise Agile Coach",
    "Consultor de Transformação Organizacional", 
    "Head de Delivery Transformation",
    "Lean Portfolio Execution Lead",
    "PMO Estratégico",
    "Transformation PMO",
    "Strategic Delivery Manager"
]

def buscar_vagas_free():
    """Busca vagas REAIS do site Vagas.com"""
    import requests
    from bs4 import BeautifulSoup
    
    vagas_encontradas = []
    
    for cargo in PALAVRAS_CHAVE:
        # Busca no Vagas.com
        url_busca = f"https://www.vagas.com.br/vagas/{cargo.replace(' ', '-').lower()}"
        
        try:
            resposta = requests.get(url_busca, timeout=10)
            if resposta.status_code == 200:
                sopa = BeautifulSoup(resposta.text, 'html.parser')
                
                # Pega os primeiros resultados
                vagas = sopa.find_all('div', class_='vagas-item')[:3]
                
                for vaga in vagas:
                    titulo = vaga.find('a', class_='vaga-title')
                    if titulo:
                        vagas_encontradas.append({
                            "titulo": titulo.text.strip(),
                            "empresa": "Ver no site",
                            "link": "https://www.vagas.com.br" + titulo['href'],
                            "data": datetime.now().strftime("%Y-%m-%d")
                        })
        except Exception as erro:
            print(f"Erro ao buscar '{cargo}': {erro}")
        
        time.sleep(2)  # Respeita o site
    
    return vagas_encontradas

def enviar_email(vagas):
    """Envia as vagas por e-mail"""
    if not vagas:
        print("⚠️ Nenhuma vaga nova encontrada hoje")
        return
    
    # Monta o corpo do e-mail
    corpo_email = f"""
    🎯 BOAS VAGAS EXECUTIVAS - {datetime.now().strftime('%d/%m/%Y')}
    
    Olá! Seu robô encontrou {len(vagas)} vagas hoje:
    
    """
    
    for vaga in vagas:
        corpo_email += f"""
    📌 {vaga['titulo']}
    🏢 Empresa: {vaga['empresa']}
    🔗 Link: {vaga['link']}
    -----------------------------------
    """
    
    corpo_email += "\nBoa sorte nas candidaturas! 🍀\nSeu robô de vagas :)"
    
    # Configura o e-mail
    msg = MIMEText(corpo_email, 'plain', 'utf-8')
    msg['Subject'] = f"✅ {len(vagas)} Vagas Executivas encontradas - {datetime.now().strftime('%d/%m')}"
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    
    try:
        # Conecta ao Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SUA_SENHA_APP)
        server.send_message(msg)
        server.quit()
        print(f"📧 E-mail enviado com sucesso para {EMAIL_DESTINO}")
    except Exception as erro:
        print(f"❌ Erro ao enviar e-mail: {erro}")

def main():
    print("🚀 Iniciando robô de vagas executivas...")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Busca as vagas
    vagas = buscar_vagas_free()
    
    # Envia o e-mail
    enviar_email(vagas)
    
    print("🏁 Robô finalizado!")

if __name__ == "__main__":
    main()

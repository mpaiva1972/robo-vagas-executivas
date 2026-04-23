# robo_raspador.py - Versão completa com raspador + fallback de links
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import json
import os

# Importa os raspadores
from indeed_scraper import buscar_vagas_indeed
from gupy_scraper import buscar_vagas_gupy

# ===== CONFIGURAÇÕES (VOCÊ MUDA AQUI) =====
SEU_EMAIL = "seuemail@gmail.com"  # ← MUDE
SUA_SENHA_APP = ""  # ← COLE SUA SENHA DO APP
EMAIL_DESTINO = "seuemail@gmail.com"  # ← MUDE

# Lista de sites para fallback (caso raspador falhe)
SITES_FALLBACK = [
    {"nome": "LinkedIn", "url": "https://www.linkedin.com/jobs/search/?keywords={palavra}&location=Brasil"},
    {"nome": "InfoJobs", "url": "https://www.infojobs.com.br/vagas.aspx?Palavra={palavra}"},
    {"nome": "Curriculum", "url": "https://www.curriculum.com.br/vagas/{palavra}"},
    {"nome": "Solides", "url": "https://www.solides.com.br/vagas?q={palavra}"}
]

PALAVRAS_CHAVE = [
    "Enterprise Agile Coach",
    "Consultor de Transformação Organizacional",
    "Head de Delivery Transformation",
    "Lean Portfolio Execution Lead",
    "PMO Estratégico",
    "Transformation PMO",
    "Strategic Delivery Manager"
]

def gerar_links_fallback():
    """Gera links de busca (seu sistema antigo) como fallback"""
    links = []
    for cargo in PALAVRAS_CHAVE:
        for site in SITES_FALLBACK:
            url = site["url"].replace("{palavra}", cargo.replace(" ", "%20"))
            links.append({
                "titulo": cargo,
                "empresa": "Clique para buscar",
                "local": site["nome"],
                "descricao": "🔍 Link de busca ativo - clique para ver vagas",
                "link": url,
                "site": f"{site['nome']} (Busca)",
                "data_coleta": datetime.now().isoformat(),
                "tipo": "fallback"
            })
    return links

def formatar_email_html(vagas_raspadas, links_fallback):
    """Formata o e-mail com duas seções: vagas reais + links"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }}
            .vagas-reais {{ background: #e8f5e9; border-left: 4px solid #4caf50; padding: 15px; margin: 20px 0; }}
            .fallback {{ background: #fff3e0; border-left: 4px solid #ff9800; padding: 15px; margin: 20px 0; }}
            .vaga-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 10px 0; background: white; }}
            .titulo {{ color: #0073b1; font-size: 16px; font-weight: bold; }}
            .empresa {{ color: #666; font-size: 14px; }}
            .descricao {{ color: #555; font-size: 13px; margin: 5px 0; }}
            .link {{ color: #4caf50; }}
            .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 11px; margin-left: 10px; }}
            .badge-real {{ background: #4caf50; color: white; }}
            .badge-fallback {{ background: #ff9800; color: white; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>🎯 RELATÓRIO DE VAGAS EXECUTIVAS</h2>
            <p>{datetime.now().strftime('%d/%m/%Y às %H:%M')}</p>
        </div>
    """
    
    # Seção de vagas raspadas (REAIS)
    if vagas_raspadas:
        html += f"""
        <div class="vagas-reais">
            <h3>✅ VAGAS REAIS ENCONTRADAS ({len(vagas_raspadas)})</h3>
            <p>Estas vagas foram coletadas automaticamente dos sites:</p>
        """
        for vaga in vagas_raspadas:
            html += f"""
            <div class="vaga-card">
                <div class="titulo">
                    📌 {vaga['titulo']}
                    <span class="badge badge-real">{vaga['site']}</span>
                </div>
                <div class="empresa">🏢 {vaga['empresa']} | 📍 {vaga.get('local', 'Remoto')}</div>
                <div class="descricao">📝 {vaga.get('descricao', 'Sem descrição')[:200]}</div>
                <div class="link">🔗 <a href="{vaga['link']}" target="_blank">Clique para se candidatar</a></div>
            </div>
            """
        html += "</div>"
    else:
        html += """
        <div class="vagas-reais">
            <h3>⚠️ NENHUMA VAGA REAL ENCONTRADA HOJE</h3>
            <p>Os raspadores não encontraram vagas novas. Os links de busca abaixo ainda funcionam!</p>
        </div>
        """
    
    # Seção de links de fallback (buscas)
    if links_fallback:
        # Agrupa por site
        por_site = {}
        for link in links_fallback:
            site = link['site']
            if site not in por_site:
                por_site[site] = []
            por_site[site].append(link)
        
        html += f"""
        <div class="fallback">
            <h3>🔍 LINKS DE BUSCA ATIVOS ({len(links_fallback)})</h3>
            <p>Clique nos links abaixo para buscar vagas diretamente nos sites:</p>
        """
        for site, links in por_site.items():
            html += f"<h4>📌 {site}</h4>"
            for link in links[:5]:
                html += f"""
                <div class="vaga-card">
                    <div class="titulo">{link['titulo']}</div>
                    <div class="link">🔗 <a href="{link['link']}" target="_blank">Buscar no {site}</a></div>
                </div>
                """
        html += "</div>"
    
    html += """
        <div style="background: #f0f0f0; padding: 15px; text-align: center; margin-top: 20px; border-radius: 8px;">
            <p>🤖 Robô de vagas executivas | Configurado para buscar diariamente às 6h</p>
            <p>💡 Dica: Salve este e-mail e use os links todos os dias!</p>
        </div>
    </body>
    </html>
    """
    
    return html

async def main():
    print("🚀 INICIANDO ROBÔ RASPADOR DE VAGAS")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    todas_vagas_raspadas = []
    
    # Tenta raspar o Indeed
    try:
        indeed_vagas = await buscar_vagas_indeed()
        todas_vagas_raspadas.extend(indeed_vagas)
        print(f"✅ Indeed: {len(indeed_vagas)} vagas")
    except Exception as e:
        print(f"❌ Indeed falhou: {e}")
    
    # Tenta raspar o Gupy
    try:
        gupy_vagas = await buscar_vagas_gupy()
        todas_vagas_raspadas.extend(gupy_vagas)
        print(f"✅ Gupy: {len(gupy_vagas)} vagas")
    except Exception as e:
        print(f"❌ Gupy falhou: {e}")
    
    # Remove duplicatas (mesmo título + mesma empresa)
    vagas_unicas = []
    chaves_vistas = set()
    for vaga in todas_vagas_raspadas:
        chave = f"{vaga['titulo']}_{vaga['empresa']}"
        if chave not in chaves_vistas:
            chaves_vistas.add(chave)
            vagas_unicas.append(vaga)
    
    print(f"\n📊 TOTAL: {len(vagas_unicas)} vagas únicas raspadas")
    
    # Gera links de fallback (sempre inclui para garantir)
    links_fallback = gerar_links_fallback()
    
    # Formata e envia e-mail
    html_email = formatar_email_html(vagas_unicas, links_fallback)
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"🎯 {len(vagas_unicas)} vagas executivas + links - {datetime.now().strftime('%d/%m')}"
    msg['From'] = SEU_EMAIL
    msg['To'] = EMAIL_DESTINO
    
    # Anexa o HTML
    msg.attach(MIMEText(html_email, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SEU_EMAIL, SUA_SENHA_APP)
        server.send_message(msg)
        server.quit()
        print(f"\n📧 E-mail enviado com sucesso para {EMAIL_DESTINO}")
    except Exception as e:
        print(f"\n❌ Erro ao enviar e-mail: {e}")
    
    return vagas_unicas

if __name__ == "__main__":
    asyncio.run(main())

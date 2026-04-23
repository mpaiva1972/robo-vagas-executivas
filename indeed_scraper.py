# indeed_scraper.py - Raspador de vagas do Indeed
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
import urllib.parse
import os

PALAVRAS_CHAVE = [
    "Enterprise Agile Coach",
    "Consultor de Transformação Organizacional",
    "Head de Delivery Transformation",
    "Lean Portfolio Execution Lead",
    "PMO Estratégico",
    "Transformation PMO",
    "Strategic Delivery Manager"
]

async def buscar_vagas_indeed():
    """Busca vagas no Indeed Brasil"""
    vagas_encontradas = []
    
    print("🔍 Iniciando busca no Indeed...")
    
    async with async_playwright() as p:
        # Navegador em modo headless (sem janela) para rodar no GitHub
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        for cargo in PALAVRAS_CHAVE:
            print(f"  Buscando: {cargo}")
            
            cargo_formatado = urllib.parse.quote(cargo)
            url = f"https://www.indeed.com.br/empregos?q={cargo_formatado}&l=Brasil"
            
            try:
                await page.goto(url, timeout=30000)
                await asyncio.sleep(3)
                
                # Aguarda os resultados ou identifica que não tem
                await page.wait_for_selector('div.job_seen_beacon', timeout=10000)
                
                # Pega os cards de emprego
                job_cards = await page.query_selector_all('div.job_seen_beacon')
                
                for card in job_cards[:5]:  # Limita a 5 por busca
                    try:
                        # Título
                        titulo_elem = await card.query_selector('h2.jobTitle a')
                        titulo = await titulo_elem.inner_text() if titulo_elem else "N/A"
                        
                        # Empresa
                        empresa_elem = await card.query_selector('span[data-testid="company-name"]')
                        empresa = await empresa_elem.inner_text() if empresa_elem else "N/A"
                        
                        # Local
                        local_elem = await card.query_selector('div[data-testid="text-location"]')
                        local = await local_elem.inner_text() if local_elem else "N/A"
                        
                        # Descrição resumida (se disponível)
                        desc_elem = await card.query_selector('div.job-snippet')
                        descricao = await desc_elem.inner_text() if desc_elem else ""
                        descricao = descricao[:300] + "..." if len(descricao) > 300 else descricao
                        
                        # Link
                        link_elem = await card.query_selector('h2.jobTitle a')
                        link = await link_elem.get_attribute("href") if link_elem else ""
                        if link and not link.startswith("https"):
                            link = "https://www.indeed.com.br" + link
                        
                        vagas_encontradas.append({
                            "titulo": titulo.strip(),
                            "empresa": empresa.strip(),
                            "local": local.strip(),
                            "descricao": descricao,
                            "link": link,
                            "site": "Indeed",
                            "data_coleta": datetime.now().isoformat()
                        })
                        
                    except Exception as e:
                        print(f"    Erro ao extrair vaga: {e}")
                    
                    await asyncio.sleep(1)
                
            except Exception as e:
                print(f"    Erro ao buscar {cargo}: {e}")
            
            await asyncio.sleep(3)  # Delay entre buscas
        
        await browser.close()
    
    print(f"  Indeed finalizado: {len(vagas_encontradas)} vagas")
    return vagas_encontradas

# Teste rápido se rodar o arquivo direto
if __name__ == "__main__":
    vagas = asyncio.run(buscar_vagas_indeed())
    for v in vagas:
        print(f"\n📌 {v['titulo']}")
        print(f"   Empresa: {v['empresa']}")
        print(f"   Link: {v['link']}")

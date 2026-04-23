# gupy_scraper.py - Busca vagas na API do Gupy
import aiohttp
import asyncio
from datetime import datetime

PALAVRAS_CHAVE = [
    "Enterprise Agile Coach",
    "Consultor de Transformação Organizacional",
    "Head de Delivery Transformation",
    "Lean Portfolio Execution Lead",
    "PMO Estratégico",
    "Transformation PMO",
    "Strategic Delivery Manager"
]

async def buscar_vagas_gupy():
    """Busca vagas no Gupy via API pública"""
    vagas_encontradas = []
    
    print("🔍 Buscando no Gupy...")
    
    async with aiohttp.ClientSession() as session:
        for cargo in PALAVRAS_CHAVE:
            print(f"  Buscando: {cargo}")
            
            # URL da API pública do Gupy
            url = "https://portal.gupy.io/api/jobs"
            params = {
                "term": cargo,
                "limit": 10,
                "offset": 0
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for job in data.get("data", []):
                            vaga = {
                                "titulo": job.get("name", "N/A"),
                                "empresa": job.get("company", {}).get("name", "N/A"),
                                "local": job.get("workplace", "N/A"),
                                "descricao": job.get("description", "")[:300] + "...",
                                "link": f"https://portal.gupy.io/job/{job.get('id', '')}",
                                "site": "Gupy",
                                "data_coleta": datetime.now().isoformat()
                            }
                            vagas_encontradas.append(vaga)
                            
                    else:
                        print(f"    Erro na API: {response.status}")
                        
            except Exception as e:
                print(f"    Erro: {e}")
            
            await asyncio.sleep(2)
    
    print(f"  Gupy finalizado: {len(vagas_encontradas)} vagas")
    return vagas_encontradas

if __name__ == "__main__":
    vagas = asyncio.run(buscar_vagas_gupy())
    print(f"\nTotal: {len(vagas)} vagas")

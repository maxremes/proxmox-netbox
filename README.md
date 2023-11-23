# Proxmox - Netbox Synkronisering

## Översikt
Detta projekt innehåller ett Python-skript för att synkronisera data från Proxmox, en servervirtualiseringshanteringsplattform, till Netbox, en infrastrukturresurshantering (IPAM/DCIM) plattform. Skriptet är avsett att automatisera processen att uppdatera Netbox med den senaste informationen om virtuella maskiner (VM) och LXC-containrar hanterade av Proxmox.

## Huvudfunktioner
- **Extrahering av VM- och LXC-data**: Skriptet hämtar detaljerad information om alla VM och LXC-containrar som körs på Proxmox, inklusive deras status, resurser (CPU, minne, disk), och nätverkskonfiguration.
- **Uppdatering av Netbox**: Informationen om varje VM och LXC synkroniseras med Netbox. Detta inkluderar uppdatering av status, tilldelning av resurser och uppdatering av nätverksinterface och IP-adresser.
- **Automatisering**: Skriptet är avsett att köras som en automatiserad uppgift, vilket minskar behovet av manuell datainmatning och säkerställer att data i Netbox alltid är aktuell.

## Tekniska Detaljer
- **Språk**: Python 3
- **Externa Bibliotek**:
  - `proxmoxer` för att interagera med Proxmox API.
  - `requests` för att göra HTTP-anrop till Netbox API.
  - `urllib3` för att hantera HTTPS-förfrågningar och varningar.

## Installation och Konfiguration
1. **Klona repo**: `git clone https://github.com/dittGithubAnvändarnamn/proxmox-netbox-sync.git`
2. **Installera beroenden**: Kör `pip install proxmoxer requests urllib3`.
3. **Konfigurera Proxmox och Netbox-åtkomst**: Uppdatera `proxmox_host`, `username`, `password`, `netbox_api_url`, och `netbox_api_token` variablerna i skriptet med dina Proxmox och Netbox-uppgifter.
4. **Kör Skriptet**: Använd `python3 proxmox-netbox-synk.py` för att köra skriptet.

## Användning
Efter att ha konfigurerat nödvändig information, kan skriptet köras manuellt eller schemaläggas för regelbunden exekvering. Detta säkerställer att din Netbox-databas speglar den aktuella statusen för dina Proxmox-resurser.

## Framtidens Utveckling
- Förbättrad felhantering och loggning.
- Stöd för fler nätverkskonfigurationer och komplexa scenarier.
- Integrering med andra verktyg och system för utökad funktionalitet.


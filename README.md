# Proxmox till Netbox Synkronisering

## Översikt
Det här projektet innehåller ett Python-skript för att synkronisera information från Proxmox, en servervirtualiseringsplattform, till Netbox, en infrastrukturresurshantering (IPAM/DCIM). Skriptet är utformat för att automatisera processen att uppdatera Netbox med den senaste informationen om virtuella maskiner (VM) och LXC-containrar hanterade av Proxmox.

## Huvudfunktioner
- **Extrahering av VM- och LXC-data**: Skriptet hämtar detaljerad information om alla VM och LXC-containrar som körs på Proxmox, inklusive deras status, resurser (CPU, minne, disk) och nätverkskonfiguration.
- **Uppdatering av Netbox**: Informationen om varje VM och LXC synkroniseras med Netbox. Detta inkluderar uppdatering av status, tilldelning av resurser och uppdatering av nätverksinterface och IP-adresser.
- **Trådhantering för Förbättrad Prestanda**: Skriptet använder Python trådhantering för att parallellt hantera flera API-förfrågningar, vilket ökar effektiviteten betydligt.
- **Caching**: För att minska belastningen på både Proxmox och Netbox servrarna och förbättra skriptets prestanda, implementeras en enkel caching-mekanism.

## Tekniska Detaljer
- **Språk**: Python 3
- **Externa Bibliotek**:
  - `proxmoxer` för interaktion med Proxmox API.
  - `requests` för HTTP-anrop till Netbox API.
  - `urllib3` för hantering av HTTPS-förfrågningar och varningar.
  - `threading` för parallell exekvering av uppgifter.

## Installation och Konfiguration
1. **Klona repot**: `git clone https://github.com/maxremes/proxmox-netbox.git`
2. **Installera beroenden**: Kör `pip install proxmoxer requests urllib3`.
3. **Konfigurera Proxmox och Netbox-åtkomst**: Uppdatera `proxmox_host`, `username`, `password`, `netbox_api_url` och `netbox_api_token` variablerna i skriptet med dina Proxmox och Netbox-uppgifter.

## Användning
Efter att ha konfigurerat nödvändig information, kan skriptet köras manuellt eller schemaläggas för regelbunden exekvering. Detta säkerställer att din Netbox-databas speglar den aktuella statusen för dina Proxmox-resurser.

## Framtidens Utveckling
- Förbättrad felhantering och loggning.
- Stöd för fler nätverkskonfigurationer och komplexa scenarier.
- Integrering med andra verktyg och system för utökad funktionalitet.

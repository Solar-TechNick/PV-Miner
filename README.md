# ☀️ PV Miner - Home Assistant Integration

[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/Solar-TechNick/PV-Miner.svg)](https://github.com/Solar-TechNick/PV-Miner/releases)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5.svg)](https://www.home-assistant.io/)
[![LuxOS](https://img.shields.io/badge/LuxOS-Compatible-orange.svg)](https://docs.luxor.tech/)

Eine vollständige Home Assistant Custom Component für nachhaltiges Bitcoin-Mining mit **Antminer S21+**, **S19j Pro** und **S19j Pro+**, betrieben mit **Solarstrom** und LuxOS-Firmware.

---

## 🚀 Features

### 🎯 Mining Control
- **Pause/Resume**: Sofortiges Deaktivieren/Aktivieren aller Hashboards
- **Solar Max**: 4200W für maximale Solarstromnutzung
- **Eco Mode**: 1500W für energieeffizientes Mining
- **Emergency Stop**: Sofortiger Stopp aller Mining-Operationen

### ⚡ Power Management
- **Power Profiles**: Max Power (+2), Balanced (0), Ultra Eco (-2), Night modes
- **Individual Control**: Separate Steuerung für jedes Hashboard (0, 1, 2)
- **Solar Integration**: Automatische Leistungsanpassung basierend auf verfügbarem Solarstrom
- **Priority System**: Konfigurierbarer Prioritäts-basierte Stromverteilung

### 📊 Real-time Monitoring
- **Performance Metrics**: Hashrate, Stromverbrauch, Effizienz, Betriebszeit
- **Temperature Monitoring**: Pro-Board und Gesamt-Temperaturüberwachung
- **Pool Status**: Aktueller Mining-Pool und Verbindungsstatus
- **Auto-refresh**: Konfigurierbare Update-Intervalle (30-60s)

---

## 🏠 Installation

### HACS (Empfohlen)

1. Öffnen Sie HACS in Home Assistant
2. Navigieren Sie zu "Integrations"
3. Klicken Sie auf die drei Punkte oben rechts und wählen Sie "Custom repositories"
4. Fügen Sie `https://github.com/Solar-TechNick/PV-Miner` als Integration hinzu
5. Suchen Sie nach "PV Miner" und installieren Sie es
6. Starten Sie Home Assistant neu

### Manuelle Installation

1. Laden Sie dieses Repository herunter
2. Kopieren Sie den `custom_components/pv_miner` Ordner in Ihr Home Assistant `custom_components` Verzeichnis
3. Starten Sie Home Assistant neu

---

## ⚙️ Konfiguration

1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **Integration hinzufügen**
3. Suchen Sie nach "PV Miner"
4. Geben Sie die Miner-Details ein:
   - **IP-Adresse**: IP Ihres Antminers (z.B. 192.168.1.210)
   - **Name**: Anzeigename (z.B. "Antminer S19j Pro+")
   - **Benutzername**: Standard ist "root"
   - **Passwort**: Standard ist "root"
5. Konfigurieren Sie Leistungsgrenzen und Prioritäten
6. Setzen Sie Update-Intervalle

---

## 🛠️ Unterstützte Hardware

| Komponente         | Beschreibung                                  |
|--------------------|-----------------------------------------------|
| 🧠 Miner           | Antminer S21+, S19j Pro, S19j Pro+ mit LuxOS |
| ☀️ Solarpanels     | Beliebige Größe je nach Anforderung          |
| 🔋 Batterie        | Optional (z. B. LiFePO4, 48V)                 |
| ⚡ MPPT-Laderegler | Victron, EPEver, etc.                         |
| 💻 Controller      | Home Assistant (jede Installation)           |

---

## 📖 Dokumentation

Für detaillierte Einrichtungsanleitungen, Automation-Beispiele und Fehlerbehebung siehe die [vollständige Dokumentation](README_INTEGRATION.md).

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Solar-TechNick/PV-Miner/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Solar-TechNick/PV-Miner/discussions)
- **Dokumentation**: [LuxOS API Docs](https://docs.luxor.tech/)

---

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz.
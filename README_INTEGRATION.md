# ☀️ PV Miner – Home Assistant Integration

Eine vollständige Home Assistant Custom Component für nachhaltiges Bitcoin-Mining mit **Antminer S21+**, **S19j Pro** und **S19j Pro+**, betrieben mit **Solarstrom** und LuxOS-Firmware.

[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Integration-41BDF5.svg)](https://www.home-assistant.io/)
[![HACS](https://img.shields.io/badge/HACS-Default-41BDF5.svg)](https://hacs.xyz/)
[![LuxOS](https://img.shields.io/badge/LuxOS-Compatible-orange.svg)](https://docs.luxor.tech/)

---

## 🚀 Features

### 🎯 Mining Control
- **Pause/Resume**: Sofortiges Deaktivieren/Aktivieren aller Hashboards
- **Solar Max**: 4200W für maximale Solarstromnutzung
- **Eco Mode**: 1500W für energieeffizientes Mining
- **Emergency Stop**: Sofortiger Stopp aller Mining-Operationen

### ⚡ Power Profiles
- **Max Power**: +2 Overclock-Profil für Spitzenleistung
- **Balanced**: Standard-Profil für optimale Effizienz
- **Ultra Eco**: -2 Underclock-Profil für minimalen Stromverbrauch
- **Manual**: -16 bis +4 individuelle Frequenzeinstellung

### 🔧 Hashboard Control
- **Individual Board Toggle**: Steuerung der Boards 0, 1 und 2 unabhängig
- **Real-time Status**: Überwachung von Temperatur, Frequenz, Spannung pro Board
- **Smart Automation**: Automatisches Board-Management basierend auf Solarstrom

### 📊 Real-time Monitoring
- **Auto-refresh**: Updates alle 30-60 Sekunden (konfigurierbar)
- **Performance Metrics**: Hashrate, Stromverbrauch, Effizienz
- **Temperature Monitoring**: Pro-Board und Gesamt-Temperaturüberwachung
- **Pool Status**: Aktueller Mining-Pool und Status

### ☀️ Solar Integration
- **Manual Power Input**: Verfügbare Solarleistung setzen (0-50000W)
- **Automatic Adjustment**: Automatische Leistungsanpassung basierend auf verfügbarem Solarstrom
- **Priority Management**: Konfigurierbarer Prioritäts-basierter Stromverteilung zwischen Minern
- **Smart Profiles**: Automatisches Profil-Switching basierend auf Solarleistung

### 🌙 Night Operations
- **Night Mode (30%)**: Leiser Betrieb mit 30% Leistung
- **Night Mode (15%)**: Ultra-leiser Betrieb mit 15% Leistung
- **Standby Mode**: Kompletter Shutdown für stille Nächte

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
1. Kopieren Sie den `custom_components/pv_miner` Ordner in Ihr Home Assistant `custom_components` Verzeichnis
2. Starten Sie Home Assistant neu
3. Die Integration ist nun verfügbar

---

## ⚙️ Konfiguration

### Grundeinrichtung
1. Gehen Sie zu **Einstellungen** → **Geräte & Dienste**
2. Klicken Sie auf **Integration hinzufügen**
3. Suchen Sie nach "PV Miner"
4. Geben Sie die Miner-Details ein:
   - **IP-Adresse**: IP Ihres Antminers (z.B. 192.168.1.210)
   - **Name**: Anzeigename (z.B. "Antminer S19j Pro+")
   - **Benutzername**: Standard ist "root"
   - **Passwort**: Standard ist "rootz"

### Leistungseinstellungen
- **Mindestleistung**: Minimale Wattzahl für den Betrieb
- **Maximalleistung**: Maximale Wattzahl für den Betrieb
- **Priorität**: Priorität für Stromverteilung (1 = höchste)

### Update-Intervalle
- **Scan-Intervall**: Wie oft Miner-Daten abgerufen werden (Standard: 30s)
- **Solar-Update-Intervall**: Wie oft Solar-Anpassungen vorgenommen werden (Standard: 10 Min)

---

## 🎛️ Verwendung

### Entitäten
Nach der Einrichtung erhalten Sie folgende Entitäten pro Miner:

**Sensoren:**
- `sensor.{miner_name}_hashrate` - Aktuelle Hashrate (TH/s)
- `sensor.{miner_name}_power_consumption` - Stromverbrauch (W)
- `sensor.{miner_name}_temperature` - Durchschnittstemperatur (°C)
- `sensor.{miner_name}_fan_speed` - Lüftergeschwindigkeit (RPM)
- `sensor.{miner_name}_efficiency` - Effizienz (J/TH)
- `sensor.{miner_name}_uptime` - Betriebszeit (s)
- `sensor.{miner_name}_mining_pool` - Aktueller Mining-Pool
- `sensor.{miner_name}_hashboard_X_temperature` - Hashboard-Temperaturen

**Schalter:**
- `switch.{miner_name}_miner` - Miner Ein/Aus
- `switch.{miner_name}_hashboard_X` - Einzelne Hashboard-Steuerung

**Eingaben:**
- `number.{miner_name}_power_limit` - Leistungsgrenze (W)
- `number.{miner_name}_frequency_offset` - Frequenz-Offset (-16 bis +4)
- `number.{miner_name}_available_solar_power` - Verfügbare Solarleistung (W)

**Auswahl:**
- `select.{miner_name}_power_profile` - Leistungsprofil-Auswahl
- `select.{miner_name}_solar_mode` - Solar-Betriebsmodus

### Services
Die Integration bietet folgende Services:

```yaml
# Leistungsprofil setzen
service: pv_miner.set_power_profile
data:
  entity_id: switch.antminer_s19j_pro_miner
  profile: solar_max

# Leistungsgrenze setzen  
service: pv_miner.set_power_limit
data:
  entity_id: switch.antminer_s19j_pro_miner
  power_limit: 3000

# Notstopp
service: pv_miner.emergency_stop
data:
  entity_id: switch.antminer_s19j_pro_miner

# Solar Maximum (4200W)
service: pv_miner.solar_max
data:
  entity_id: switch.antminer_s19j_pro_miner

# Eco-Modus (1500W)  
service: pv_miner.eco_mode
data:
  entity_id: switch.antminer_s19j_pro_miner

# Mining Pool wechseln
service: pv_miner.set_pool
data:
  entity_id: switch.antminer_s19j_pro_miner
  pool_url: "stratum+tcp://pool.example.com:4444"
  pool_user: "your_username"
  pool_password: "x"
  priority: 0
```

### Automation Beispiele

**Automatische Solar-Anpassung:**
```yaml
automation:
  - alias: "Solar Mining Adjustment"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power_production
        above: 4000
    action:
      - service: pv_miner.solar_max
        target:
          entity_id: switch.antminer_s19j_pro_miner

  - alias: "Low Solar Power"
    trigger:
      - platform: numeric_state
        entity_id: sensor.solar_power_production
        below: 1500
    action:
      - service: pv_miner.eco_mode
        target:
          entity_id: switch.antminer_s19j_pro_miner
```

**Nacht-Modus:**
```yaml
automation:
  - alias: "Night Mode"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: pv_miner.set_power_profile
        data:
          entity_id: switch.antminer_s19j_pro_miner
          profile: night_30
```

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

## 🔧 Entwicklung

### Voraussetzungen
- Python 3.11+
- Home Assistant Development Environment
- LuxOS-kompatible Antminer

### Tests ausführen
```bash
pytest __tests__/
```

### Beitragen
1. Fork des Repositories
2. Feature-Branch erstellen (`git checkout -b feature/amazing-feature`)
3. Änderungen committen (`git commit -m 'Add amazing feature'`)
4. Branch pushen (`git push origin feature/amazing-feature`)
5. Pull Request öffnen

---

## 📝 Lizenz

Dieses Projekt steht unter der MIT-Lizenz. Siehe [LICENSE](LICENSE) für Details.

---

## 🙏 Danksagungen

- [Luxor Technologies](https://luxor.tech/) für LuxOS-Dokumentation
- [Home Assistant](https://home-assistant.io/) Community
- Alle Mitwirkenden zu diesem Projekt

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/Solar-TechNick/PV-Miner/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/Solar-TechNick/PV-Miner/discussions)
- **Dokumentation**: [LuxOS API Docs](https://docs.luxor.tech/)
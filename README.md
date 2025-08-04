# ☀️ Solar Bitcoin Miner – Home Assistant Integration

Ein Open-Source-Projekt für nachhaltiges Bitcoin-Mining mit **Antminer S21+**, **S19j Pro** und **S19j Pro+**, betrieben ausschließlich mit **Solarstrom** und vollständig integriert in **Home Assistant**.

---

## 🌱 Projektübersicht

Dieses Projekt zeigt, wie man energieintensives Bitcoin-Mining durch intelligente Steuerung und Echtzeitüberwachung in ein nachhaltiges Konzept überführt – **autark, effizient und umweltbewusst**.

Durch die Anbindung an **Home Assistant** erhältst du:
- Echtzeit-Status deiner Miner
- Automatische Steuerung nach Sonnenverlauf & Batterieladung
- Integration ins Smart Home (z. B. Benachrichtigungen, Ausfallschutz)
- Energieoptimiertes Mining ganz ohne Netzstrom

---

## ⚙️ Unterstützte Hardware

| Komponente         | Beschreibung                                  |
|--------------------|-----------------------------------------------|
| 🧠 Miner           | Antminer S21+, S19j Pro, S19j Pro+             |
| ☀️ Solarpanels     | Größe je nach Region & Minerleistung          |
| 🔋 Batterie        | Optional (z. B. LiFePO4, 48 V) für Nachtbetrieb |
| ⚡ MPPT-Laderegler | z. B. Victron, EPEver                         |
| 💻 Controller      | Raspberry Pi, Home Assistant Yellow, ESP32     |

---

## 🏡 Home Assistant Integration

### 📦 Funktionen

- MQTT- und REST-basierte Live-Daten der Miner
- Energie- & Temperaturüberwachung
- Automationen für Start/Stopp je nach Sonnenstand & Akkuladung
- Kompatibel mit ESPHome, Node-RED, Zigbee & mehr

### 🔧 Beispiel-Sensoren (`configuration.yaml`)

```yaml
sensor:
  - platform: rest
    name: "Antminer Hashrate"
    resource: "http://192.168.1.150/api/status"
    value_template: "{{ value_json.hashrate }}"
    unit_of_measurement: "TH/s"

  - platform: mqtt
    name: "PV Leistung"
    state_topic: "solar/pv_power"
    unit_of_measurement: "W"

  - platform: mqtt
    name: "Batterieladung"
    state_topic: "solar/battery_soc"
    unit_of_measurement: "%"

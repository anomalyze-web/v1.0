# Anomalyze: Multi-Dimensional Network Forensic Engine

**Anomalyze** is an advanced analytics platform designed to detect complex security threats across telecommunication and network infrastructures. Unlike standard log parsers, Anomalyze correlates data from **Call Detail Records (CDR)**, **Internet Protocol Detail Records (IPDR)**, and **Firewall Logs** to identify sophisticated threats that span multiple domains.

The engine powers **52+ forensic algorithms** and integrates **7 specialized Machine Learning models** to flag anomalies ranging from SIM cloning to covert DNS tunneling.

---

## The AI Core: Machine Learning Modules

Anomalyze moves beyond static rule-based detection by employing ML models to catch zero-day anomalies and behavioral deviations:

* **DNS Tunneling Detection:** Identifies covert data exfiltration attempts hiding within DNS queries.
* **Behavioral Baselining:** Establishes "normal" user behavior profiles in firewall logs to flag subtle deviations.
* **IP Clustering Detection:** Uses unsupervised learning to detect coordinated botnet-like behavior across multiple IPs.
* **Data Transfer Pattern Tracking:** Classifies network traffic to spot anomalous volume spikes indicative of data theft.
* **Time-Based Access Patterns:** Learns typical user login hours to detect "impossible" or off-hour access.
* **Burst Call Detection:** Identifies rapid-fire, high-frequency call patterns often associated with robocalling or fraud.
* **HTTP Status Code Analysis:** Detects scanning attacks and server misconfigurations via status code distribution anomalies.

---

## The Co-Relation Engine (Cross-Domain Analysis)

*The "Wow Factor" of Anomalyze is its ability to connect the dots between distinct log sources.*

* **SIM Swap Behavior:** Correlates SIM card changes (CDR) with sudden shifts in IP activity or location (IPDR).
* **Insider Threat Detector:** Flags employees accessing suspicious resources combined with off-hour login attempts.
* **Geo-Location Anomaly:** Detects "impossible travel" by comparing physical call locations with simultaneous network login locations.
* **Device Spoofing:** Identifies mismatches between MAC addresses and IP usage patterns across sessions.

---

## Domain-Specific Analysis Modules

### CDR (Telecom Forensics)
* **Identity Fraud:** SIM Swapping, SIM Cloning, Number Morphing.
* **Movement Tracking:** Tower Jumping, Roaming Mismatch Detector.
* **Traffic Anomalies:** Call Spikes, Scattered Calls, Toll-Free Abuse.

### IPDR (Network Forensics)
* **Threat Intel:** Blacklisted IP Matcher, GeoIP vs WHOIS Mismatch.
* **Device Forensics:** IMEI-Multiple MSISDNs Analyzer, Shared IP Multi-User Finder.
* **Protocol Auditing:** Port-Protocol Anomaly Detector, VoIP Traffic Identifier.

### Firewall & Security
* **Intrusion Detection:** Repeated Failed Logins, Firewall Bypass Detection.
* **Traffic Monitoring:** Non-Server Traffic Monitor, Dormant Device Bandwidth Use.
* **Anomalies:** MAC-IP Mismatch, Off-Hour Activity Detection.

---

## Technology Stack

* **Core Engine:** Python 3.10+
* **Data Processing:** Pandas, NumPy (Vectorized analysis for millions of rows)
* **Machine Learning:** Scikit-Learn, TensorFlow
* **Visualization:** Streamlit (Interactive Dashboard), Plotly
* **Database:** SQLite

---

## Working Video
[Click here to watch the video demo](https://drive.google.com/file/d/1yXVqtBrPK6BNLVQ63t3xly8E6VLGkYpn/view?usp=drive_link)

## Live Demo
[Click here to check out Anomalyze](https://anomalyze.streamlit.app/)

## Interface Gallery
| **CDR ANALYSIS** | **IPDR Analysis** | **Firewall Analysis** | **Correlation**
|:---:|:---:|:---:|:---:|
| ![CDR](https://github.com/anomalyze-web/v1.0/blob/main/live_demo/cdr.png?raw=true) | ![IPDR]([link_to_image.png](https://github.com/anomalyze-web/v1.0/blob/main/live_demo/ipdr.png?raw=true)) | ![Firewall]([link_to_image.png](https://github.com/anomalyze-web/v1.0/blob/main/live_demo/firewall.png?raw=true)) | ![Correlation]([link_to_image.pn](https://github.com/anomalyze-web/v1.0/blob/main/live_demo/Correlation.png?raw=true)g) |

---

## Contributors

**The Anomalyze Team**
* **Ananya Ahuja**
* **Palak**
* **Vanshika Raj Dhalwan**
* **Saanvi**

---

## License

**Copyright (c) 2025 The Anomalyze Team.**
This software and its associated files are proprietary and confidential. Unauthorized copying, distribution, or modification is strictly prohibited.

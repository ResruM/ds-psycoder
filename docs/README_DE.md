<div align="center">

# 🧠 Amazing PsyCoder 💻

> Damit sich psychologische Forschende stärker auf ihre Forschungsfragen konzentrieren können – statt auf Code.

[![Version](https://img.shields.io/badge/version-v1.4.0-2563eb.svg)](../amazing-psycoder/SKILL.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../LICENSE)
[![DeepSeek](https://img.shields.io/badge/DeepSeek-Driven-4D6BFE)](https://www.deepseek.com)
[![DeepSeek Harness](https://img.shields.io/badge/DeepSeek%20Harness-Skill-2563eb)](https://github.com/deepseek-ai)
[![DeepSeek API](https://img.shields.io/badge/DeepSeek%20API-ds--psycoder-0ea5e9)](https://api-docs.deepseek.com)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB)](https://www.python.org/)
[![agentskills.io](https://img.shields.io/badge/agentskills.io-standard-333)](https://agentskills.io)
[![Stars](https://img.shields.io/github/stars/ResruM/ds-psycoder?style=social)](https://github.com/ResruM/ds-psycoder)

[**简体中文**](../README.md) · [**繁體中文**](README_ZH-HANT.md) · [**English**](README_EN.md) · [**日本語**](README_JA.md) · [**Deutsch**](README_DE.md) · [**Français**](README_FR.md)

<br>

[📖 Warum](#-warum-es-dieses-projekt-gibt) · [👥 Für Wen](#-für-wen) · [⚡ Installation](#-installation) · [🚀 Schnellstart](#-schnellstart) · [🧪 Experiment](#-experiment-programmierung) · [📊 Datenanalyse](#-datenanalyse) · [🎬 Demo](#-demo) · [📂 Dateistruktur](#-dateistruktur)

</div>

<br>

## 📖 Warum es dieses Projekt gibt

<h3 align="center">🔍 Häufige Herausforderungen von der Studienplanung bis zur Datenanalyse</h3>

🔬 Um eine Forschungsidee in ein Experiment zur Datenerhebung zu überführen, sind häufig Kenntnisse in Python, JavaScript oder MATLAB erforderlich.<br>
📦 Vorhandener Laborcode kann bei einer veränderten Laufzeitumgebung ausfallen; Abhängigkeiten und Kernlogik sind zudem oft schwer zu warten.<br>
📊 Werden statistische Methoden vor allem aus Gewohnheit gewählt, lässt sich ihre Passung zu Forschungsfrage, Variablentyp und Datenstruktur schwer begründen.<br>
🔁 Ohne dokumentierte Softwareversionen und Abhängigkeiten kann eine Analyse auf einem anderen Rechner schwer reproduzierbar sein.<br>
✂️ Sind Experimentdesign und Analyseplanung nicht aufeinander abgestimmt, kann sich erst nach der Datenerhebung zeigen, dass das Design die geplante Analyse nicht unterstützt.

<h3 align="center">🧱 Zwei zentrale Schwierigkeiten bei der Durchführung von Forschung</h3>

**Erstens: Experiment-Programmierung.** Um eine Hypothese zu prüfen, muss das Design in ein Programm übertragen werden. PsychoPy Builder ist für manche komplexen Designs möglicherweise nicht flexibel genug; Coder erfordert Python, jsPsych JavaScript und Timeline-Logik, Psychtoolbox MATLAB und Kenntnisse zur Bildschirmsynchronisation. RT-Beginn, Tastenbelegung und Datensicherung nach einer Unterbrechung müssen ausdrücklich festgelegt und einzeln geprüft werden.

**Zweitens: Datenanalyse.** Die Analyseplanung sollte möglichst vor der Datenerhebung beginnen und anschließend an der tatsächlichen Datenstruktur umgesetzt werden. Passt bei einem Within-Subject-Design ein gepaarter t-Test oder ein gemischtes Modell? Wie wird Genauigkeit nahe der Obergrenze modelliert? Wie lässt sich die Methodenwahl begründen? Ist das Ergebnis auf einem anderen Rechner reproduzierbar? Diese Entscheidungen hängen von Forschungsziel, Datenhierarchie und Softwareumgebung ab.

Diese Herausforderungen betreffen nicht nur das Programmieren, sondern auch Studiendesign, statistische Inferenz, Datenmanagement und Reproduzierbarkeit.

<h3 align="center">✨ Wie Amazing PsyCoder unterstützt</h3>

Du kannst mit einer Experimentidee, einem vorhandenen Design oder bestehenden Daten beginnen. Amazing PsyCoder unterstützt schrittweise bei der Bestätigung der Forschungsregeln, der Codeerzeugung und der Fehlersuche. Bei Bedarf stellst du weiterhin Konfigurationen, Datenbeschreibungen, Quellen für Ausschlussregeln und Ausführungsprotokolle bereit. KI-Ausgaben allein gelten nicht als „bereit zur Datenerhebung“ oder „publikationsbereit“: Das Experiment muss auf dem Erhebungsrechner getestet und die Analyse tatsächlich ausgeführt und geprüft werden.

Amazing PsyCoder besteht aus 7 Skills—einem Einstiegsskill und 6 Fachskills—und folgt dem offenen Standard [agentskills.io](https://agentskills.io). Diese Skills werden von DeepSeek angetrieben: Sie lassen sich sowohl in DeepSeek Harness (dsh) installieren als auch mit `ds_psycoder.py` direkt über die DeepSeek API aufrufen. Claude Code, Codex, Hermes und OpenClaw werden dafür nicht mehr benötigt und nicht mehr unterstützt.

Zeit für die Forschung. Nicht für die Technik.

---

## 👥 Für Wen

- 🎓 Psychologie-Studierende und Doktoranden, die ein Experiment programmieren müssen oder bald werden
- 🧠 Forschende in kognitiver, Verhaltens- oder Sozialpsychologie
- 😵‍💫 Forschende, die wiederholt Probleme mit RT, Randomisierung oder Bedingungstabellen haben und typische Risiken systematisch prüfen möchten
- 📊 Wer nach der Datenerhebung unsicher ist, welche Statistik die richtige ist — und ein durchdachtes Analyseverfahren möchte
- 🐍 PsychoPy · 🌐 jsPsych · 🧮 Psychtoolbox / MATLAB Nutzer

---

## ⚡ Installation

Empfohlen ist der mitgelieferte Installer im Repository. Er prüft zuerst alle 7 Skills; schlägt er fehl, werden die vorherigen Dateien wiederhergestellt.

```bash
git clone https://github.com/ResruM/ds-psycoder
cd ds-psycoder
```

**DeepSeek Harness (empfohlen)**

```bash
python ds_psycoder.py install
# gleichwertige Schreibweise: ./install.sh deepseek
```

Installiert nach `$DSH_HOME/skills` (Standard: `~/.dsh/skills`). Beschreibe anschließend in einer `dsh web`- oder `dsh tui`-Sitzung direkt deine Aufgabe; DeepSeek ordnet anhand der description den passenden Skill zu.

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File amazing-psycoder\install.ps1
```

**DeepSeek CLI (ohne Bindung an einen Agent-Host)**

```bash
python ds_psycoder.py doctor
python ds_psycoder.py run "Baue mir ein Stroop-Experiment"
```

Wenn du die DeepSeek API direkt aufrufen möchtest, setze `DEEPSEEK_API_KEY` und verwende das api-Backend:

```bash
python ds_psycoder.py run --backend api --workdir ./study "Analysiere diese Daten"
```

<details>
<summary><b>Projektinstallation, benutzerdefinierte Verzeichnisse und Installationsprüfung</b></summary>

<br>

```bash
./install.sh --scope project --project-dir /path/to/study
./install.sh --target /custom/skills
./install.sh --check
python ds_psycoder.py check --target /custom/skills
```

Eine Projektinstallation schreibt nach `<project>/.dsh/skills`. Das Installationsskript `./install.sh`, die PowerShell-Version `install.ps1` und `ds_psycoder.py` sind äquivalent. Weitere Hinweise siehe
[`PLATFORMS.md`](../amazing-psycoder/PLATFORMS.md).

</details>

---

## 🚀 Schnellstart

Beschreibe nach der Installation direkt in einer DeepSeek-Harness-Sitzung, was du vorhast (alternativ mit `python ds_psycoder.py run "..."`):

> "Ich möchte eine Stroop-Aufgabe machen, rot/grün/blau, Tastenreaktion" → startet automatisch das Experiment-Design

> "Hilf mir bei der Stroop-Datenanalyse: Unterscheiden sich kongruente und inkongruente RTs?" → startet automatisch das Analyse-Design

> "Prüfe diesen Experimentcode, besonders RT-Beginn und Datenspeicherung" → startet automatisch die Codeprüfung

In der Regel musst du keinen Fachskill auswählen. Der Einstiegsskill wählt anhand der Anfrage Design, Codeerzeugung oder Prüfung. Wenn unklar ist, ob du ein Experiment erstellen oder Daten analysieren möchtest, fragt er zunächst nach.

---

## 🧪 Experiment-Programmierung

Von der ersten Idee zum Experimentcode, der getestet werden kann — in drei Schritten: Design, Code, Prüfung.

### Skills

| # | Skill | Aufgabe | Wichtige Details |
|---|-------|---------|------------------|
| ① | **Design** `psy-exp-designer` | Aus einer Experiment-Idee eine komplette Designspezifikation machen | 5-Phasen-Bestätigung. Phase 2 generiert eine Trial-Fenster-Zeitlinie — Dauer, Tasten, RT-Startpunkt auf einen Blick. 5 harte Gates. 38 Paradigmen-Referenzen |
| ② | **Code** `psy-exp-coder` | Aus der Designspezifikation lauffähigen Code generieren | 4-Schichten-Prioritätsarchitektur. Vor der Übergabe prüft ein 10-Punkte-Qualitätstor Timing, Reaktionen, Speichern, Aufräumen, Abhängigkeiten und weitere blockierende Risiken |
| ③ | **Prüfung** `psy-exp-reviewer` | Vergleicht Code und bestätigtes Design | Ohne protokollierten Test auf dem Erhebungsrechner gibt es keine Freigabe zur Datenerhebung |

### Plattformen

| Plattform | Besonderheit |
|-----------|-------------|
| 🐍 **[PsychoPy](https://psychopy.org/)** | Python-Experimente im Labor; das Timing muss auf dem Zielrechner geprüft werden |
| 🌐 **[jsPsych](https://www.jspsych.org/)** | Browser- und Online-Experimente; Tests im echten Browser und auf Teilnehmergeräten sind nötig |
| 🧮 **[Psychtoolbox](https://psychtoolbox.org/)** | MATLAB/Octave-Experimente mit genauer Anzeige- und Gerätesteuerung; Synchronisation und Hardwarekalibrierung bleiben nötig |

### Referenzen für Experimentdesigns

**38 Referenzen für Experimentdesigns**, jeweils einheitlich aufgebaut: Wann verwenden → Kernlogik → Muss bestätigt werden → Nicht voraussetzen → Trial-Fenster-Zeitlinie → Bedingungstabelle → Datenanalyse → Varianten & Referenzen.

Das bedeutet **nicht**, dass 38 × 3 Generatoren auf allen drei Plattformen auf echten Geräten verifiziert wurden.

| Kategorie | Paradigmen |
|-----------|-----------|
| 🎯 **Aufmerksamkeit & Inhibitionskontrolle** | Stroop · Eriksen Flanker · Simon · Go/No-go · Stop-signal · ANT · Posner Cuing · Visual Search · Dot-probe · Navon · CPT · Antisaccade |
| 🧠 **Gedächtnis & Arbeitsgedächtnis** | N-back · Sternberg · Corsi Blocks · Change Detection · Drag and Drop |
| 🔄 **Exekutive Funktionen & kognitive Flexibilität** | Task Switching · WCST · Choice RT |
| 👥 **Soziale Kognition & Emotion** | Cyberball · Climate Reflection · Phone a Friend · Rating · Priming · IAT · EAST |
| 💰 **Entscheidung & Belohnung** | BART · Delay Discounting · Rating to Choice · Ultimatum Game |
| 👁️ **Wahrnehmung & Psychophysik** | Psychophysics Staircase · Multisensory Nature · Mental Rotation |
| 🌱 **Entwicklung & individuelle Unterschiede** | Children Flanker · Bilingual Stroop · Numerical Stroop · Writing Distraction |

---

## 📊 Datenanalyse

Eine Analyse kann vor der Datenerhebung geplant und nach Vorliegen der Daten weiter umgesetzt werden: Analyseplan erstellen, Code erzeugen und ausgeführte Ergebnisse prüfen.

### Skills

| # | Skill | Aufgabe | Wichtige Details |
|---|-------|---------|------------------|
| ④ | **Analyse-Design** `psy-ana-designer` | Ausgehend von der wissenschaftlichen Frage ein vollständiges Analysekonzept entwerfen | In fünf Phasen werden Dateiorganisation sowie die Hierarchie von Personen, Stimuli und Sitzungen bestätigt. Phase 3 vergleicht nur entscheidungsrelevante Unterschiede; die vollständigen 12 Dimensionen werden nur bei wirklich gleichwertigen Alternativen oder folgenreichen Entscheidungen genutzt |
| ⑤ | **Analyse-Code** `psy-ana-coder` | Aus dem Analysekonzept reproduzierbare Skripte generieren | Phase-0-Validierung → R/Python bestätigen → 12-Schritt-Generierung. 10-Punkte-Qualitätstor. R: tidyverse/lme4/ggplot2. Python: pandas/statsmodels/seaborn. Alles Config-gesteuert |
| ⑥ | **Analyse-Audit** `psy-ana-reviewer` | Trennt statische Codeprüfung von der Prüfung ausgeführter Ergebnisse | Eine statische Prüfung reicht höchstens für `ready_for_execution`. `ready_for_publication` erfordert zusätzlich einen erfolgreichen Lauf in sauberer Umgebung sowie geprüfte Logs, Tabellen, Abbildungen, Abhängigkeiten und Umgebungsdaten |

### Analysesprachen und Laufzeitumgebungen

| Sprache und Laufzeitumgebung | Besonderheit |
|-----------|-------------|
| 📊 **[R](https://www.r-project.org/)** | Statistische Modellierung und wissenschaftliche Berichte, etwa mit lme4, ggplot2, Quarto und R Markdown |
| 🐍 **[Python](https://www.python.org/)** | Allgemeine Datenverarbeitung, statistische Analyse, Visualisierung und Jupyter-Workflows |

### Analysemethoden

**60 Methodenreferenzen und 48 Diagrammreferenzen** helfen bei der Suche nach Kandidaten; sie sind keine automatische Vorschrift. Verglichen werden die Punkte, die die konkrete Entscheidung ändern können. Der vollständige 12-Dimensionen-Vergleich ist nur für tatsächlich gleichwertige Alternativen oder besonders folgenreiche Entscheidungen vorgesehen.

| Kategorie | Methoden (Beispiele) |
|-----------|---------------------|
| **Mittelwertsvergleiche** | Gepaarter/unabhängiger t-Test, Within-/Between-Subject-ANOVA, gemischte ANOVA, ANCOVA, MANOVA |
| **Gemischte Modelle** | Lineares gemischtes Modell (LMM), logistisches gemischtes Modell (GLMM), Gamma-GLMM, gekreuzte Zufallseffekte |
| **Mediation & Moderation** | Mediationsanalyse, Moderationsanalyse, moderierte Mediation, Strukturgleichungsmodelle |
| **Regression & Längsschnitt** | Multiple Regression, Quantilsregression, Wachstumskurven, Cross-Lagged-Panel, Zeitreihen |
| **Korrelation & Klassifikation** | Pearson/Spearman-Korrelation, Repeated-Measures-Korrelation, Chi-Quadrat-Test, kanonische Korrelation |
| **Nonparametrisch & Robust** | Wilcoxon, Friedman, Permutationstests, Bootstrap, robuste Regression |
| **Bayes-Statistik** | Bayes-t-Test, Bayes-ANOVA, bayesianisches gemischtes Modell |
| **Messung & Skalierung** | Reliabilitätsanalyse (α/ω/ICC), explorative/konfirmatorische Faktorenanalyse, multidimensionale Skalierung |
| **Signalentdeckung & Diagnostik** | d', ROC-Kurve, psychometrische Funktion |
| **RT- & Entscheidungsmodellierung** | Ex-Gaussian-Verteilung, Drift-Diffusions-Modell (DDM) |
| **Metaanalyse & Power** | Metaanalyse, Poweranalyse, Äquivalenztests |
| **Spezielle Verfahren** | Multiple Imputation, LASSO/Ridge, Netzwerkanalyse, Clusteranalyse, latente Klassenanalyse |

---

## 🎬 Demo

### 🐍 PsychoPy — Stroop-Aufgabe

> "Ich möchte eine Stroop-Aufgabe, rote/grüne/blaue Schrift, Tastendruck beurteilt die Druckfarbe, 50:50 kongruent:inkongruent, 2 Blöcke mit je 60 Durchgängen"

```
Nutzer           ❯ Ich möchte eine Stroop-Aufgabe

Amazing PsyCoder ❯ 🟢 Phase 1/5 · Diagnose
                   Paradigma Stroop · Plattform PsychoPy bestätigen?

Nutzer           ❯ Ja, PsychoPy.

Amazing PsyCoder ❯ 🟢 Phase 2/5 · Trial-Fenster + Antwortregeln (kritisch)
                   Tintenfarben → f=Rot j=Grün k=Blau. Trial-Zeitlinie:
                      Window 1: Fixation            Window 2: Stimulus             Window 3: Pause     
                   ┌──────────────────────┐      ┌──────────────────────┐      ┌──────────────────────┐
                   │                      │      │                      │      │                      │
                   │          +           │  →   │     Rot (grün)      │  →   │                      │
                   │                      │      │                      │      │                      │
                   └──────────────────────┘      └──────────────────────┘      └──────────────────────┘
                            500ms                         2000ms                        500ms          
                         keine Reak.                    f / j / k                    keine Reak.       
                                                       ← RT-Start                                     

                      Window 4: Feedback   
                   ┌──────────────────────┐
                   │                      │
                   │       Richtig!       │
                   │                      │
                   └──────────────────────┘
                            1000ms         
                         keine Reak.       
                   Gate 1 ✅ Fenster vollständig, Antwort-Mapping bestätigt

Nutzer           ❯ Zeitlinie und Tasten passen. ITI 400-800ms zufällig.

Amazing PsyCoder ❯ 🟢 Phase 3/5 · Bedingungen
                   Kongruent:inkongruent = 60:60 → 120-Trial Bedingungstabelle
                   Gate 2 ✅ Bedingungsspalten ausgefüllt

Amazing PsyCoder ❯ 🟢 Phase 4/5 · Block-Struktur
                   2 Blöcke × 60 Trials · Feedback nur im Übungsblock
                   Gate 3 ✅ Config hat null [MISSING]

Amazing PsyCoder ❯ 🟢 Phase 5/5 · Finale Prüfung
                   ┌────────────────────────────────────────────────────────┐
                   │ Design-Entscheidungsregister                           │
                   │ Paradigma Stroop · Plattform PsychoPy  ← Benutzer      │
                   │ Tasten f/j/k · 50:50 kongruent         ← Benutzer      │
                   │ ITI 400-800ms zufällig                 ← Benutzer      │
                   │ Trial-Zeitlinie 4 Fenster              ← Konvention    │
                   └────────────────────────────────────────────────────────┘
                   Gate 5 ✅ Alle bestätigt → Weiter zur Code-Generierung

Nutzer           ❯ Generieren.

Amazing PsyCoder ❯ ✅ stroop_task.py + README.md generiert
                   Parameter oben · CJK-Schriftart gesetzt · Inkrementelles Speichern
                   → Automatisch zum Code-Audit

Amazing PsyCoder ❯ 🔍 Die statische Codeprüfung fand kein blockierendes Problem.
                   Der Test auf dem Erhebungsrechner kann beginnen; noch keine Datenerhebung.

Nutzer           ❯ Start/Ende, Kurzlauf, Datenintegrität und Wiederherstellung wurden geprüft.

Amazing PsyCoder ❯ 🔍 Laufprotokoll und gespeicherte Daten wurden geprüft.
                   Bereitschaft: ready_for_collection
                   Die Datenerhebung kann beginnen.
```

### 📊 R — Stroop-Datenanalyse

> "Hilf mir mit den Stroop-Daten: Unterscheiden sich die RTs zwischen kongruenten und inkongruenten Bedingungen?"

```
Nutzer           ❯ Hilf mir mit den Stroop-Daten: kongruente vs. inkongruente RTs?

Amazing PsyCoder ❯ 🟢 Phase 1/5 · Experiment & wissenschaftliche Frage verstehen
                   Bitte gib die Experiment-Config an oder beschreibe das Design

Nutzer           ❯ Within-Subject, UV: condition(kongruent/inkongruent), AV: rt+acc. 30 Vpn

Amazing PsyCoder ❯ 🟢 Phase 2/5 · Datenstruktur verstehen
                   Wie sind die Daten gespeichert? Eine Datei pro Vpn oder zusammengefasst?

Nutzer           ❯ Eine CSV pro Vpn, Benennung sub-001_stroop.csv
                   Spalten: subject_id, stimulus, condition, rt, acc, trial

Amazing PsyCoder ❯ Sind die Stimuli pro Person verschieden, oder sieht dieselbe
                   Stimulusmenge mehrere Personen?

Nutzer           ❯ Alle sehen dieselben 60 Farb-Wort-Kombinationen und haben
                   wiederholte Trials.

Amazing PsyCoder ❯ Bestätigt: Wiederholungen innerhalb von Person und Stimulus.
                   Gate 2 ✅

Amazing PsyCoder ❯ 🟢 Phase 3/5 · Zuerst Zielgröße festlegen, dann Methode wählen
                   Primäre Zielgröße: mittlere RT-Differenz in der Population,
                   inkongruent minus kongruent.

                   Primäres RT-Modell:
                   rt ~ condition + (1 + condition | subject_id) + (1 | stimulus)

                   Genauigkeit kann ergänzend mit einem binomialen gemischten Modell
                   untersucht werden. Ein gepaarter t-Test ist einfacher, beantwortet
                   aber eine aggregierte Frage auf Basis von Personenmittelwerten.
                   Falls die Zufallseffekte nicht stabil schätzbar sind, wird nach einer
                   vorher festgelegten Reihenfolge vereinfacht und die Diagnose berichtet.

Nutzer           ❯ Zielgröße, Formel und Personen-/Stimulus-Hierarchie bestätigt.
                   Gemischtes RT-Modell, Genauigkeit als Zusatzanalyse.

Amazing PsyCoder ❯ Gate 3 ✅ Zielgröße, Formel, Hierarchie und Alternativen bestätigt

Amazing PsyCoder ❯ 🟢 Phase 4/5 · Bereinigung, Laufzeitumgebung und Ausgaben
                   RT-, Fehlwert- und Ausschlussregeln aus Aufgabenbeschreibung
                   oder Präregistrierung angeben. Keine festen Grenzwerte ohne Begründung.

Nutzer           ❯ Laut Präregistrierung nutzt die primäre RT-Analyse nur korrekte
                   Trials mit vorhandener RT. Keine festen RT-Grenzen, SD-Trimmung
                   oder automatischen Personenausschlüsse. Zusätzlich eine log-RT-
                   Sensitivitätsanalyse. Das Labor nutzt R 4.4.1, renv.lock und R Markdown.

Amazing PsyCoder ❯ 🟢 Phase 5/5 · Finale Prüfung
                   ┌──────────────────────────────────────────────────┐
                   │ Analyse-Entscheidungsregister                     │
                   │ Fragestellung: kongruent vs. inkongruent  ← Nutzer│
                   │ Formel: Personen-Steigung + Stimulus-Intercept    │
                   │ Bereinigung: Präregistrierung + Zählprotokoll     │
                   │ Umgebung: R 4.4.1 + renv.lock            ← Nutzer│
                   │ Ausgabe: Effekt, Intervall, Diagnose, Grafik     │
                   └──────────────────────────────────────────────────┘
                   Gate 5 ✅ analysis_config.yaml gespeichert → Code-Generierung

Nutzer           ❯ Generieren.

Amazing PsyCoder ❯ ✅ analysis.R + report.Rmd + renv.lock generiert
                   Abhängigkeiten erfasst · statische Prüfung abgeschlossen

Amazing PsyCoder ❯ 🔍 Bereitschaft: ready_for_execution
                   Der Code kann laufen; die Ergebnisse sind noch nicht publikationsbereit.

Nutzer           ❯ Ausführung in sauberer Umgebung mit Log, Tabellen, Grafiken und Versionen.

Amazing PsyCoder ❯ 🔍 Ausgaben geprüft · Bereitschaft: ready_for_publication
```

---

## 📂 Dateistruktur

```text
amazing-psycoder-skills/
├── ds_psycoder.py                     ← DeepSeek CLI (Installation / Prüfung / Ausführung)
├── amazing-psycoder/                  ← Haupteinstieg (v1.4.0)
│   ├── SKILL.md                       ← Routing und globale Regeln
│   ├── PLATFORMS.md · install.sh · install.ps1  ← Plattformhinweise und Installer
│   ├── STANDALONE.md                  ← Direkte Agent-Nutzung
│   ├── PSYCODER_STUDIO.md             ← Website-Integration
│   ├── runtime/                       ← Website-Verträge und Funktionsumfang
│   ├── scripts/ · tests/              ← Automatische Prüfungen
│   ├── requirements-dev.txt           ← Validierungsabhängigkeiten
│   │
│   │   # 🧪 Experiment-Programmierung
│   ├── psy-exp-designer/              ← ① Experiment-Design (5 Phasen + 38 Referenzen)
│   ├── psy-exp-coder/                 ← ② Experiment-Code (PsychoPy/jsPsych/Psychtoolbox)
│   └── psy-exp-reviewer/              ← ③ Experiment-Codeprüfung
│   │
│   │   # 📊 Datenanalyse
│   ├── psy-ana-designer/              ← ④ Analyse-Design (60 Methoden + 48 Diagrammreferenzen)
│   ├── psy-ana-coder/                 ← ⑤ Analyse-Code (R/Python)
│   └── psy-ana-reviewer/              ← ⑥ Analyse-Code- und Ausgabeprüfung
│
├── docs/                              ← Übersetzte READMEs (繁/英/日/德/法)
├── .github/                           ← Automatische Tests
└── README.md                          ← Startseite auf vereinfachtem Chinesisch
```

---

<div align="center">

💡 Ideen oder Vorschläge? Schreib an [tangdingyi04@outlook.com](mailto:tangdingyi04@outlook.com)<br>
🪄 Made by [soupandpsy](https://github.com/soupandpsy) · MIT License

</div>

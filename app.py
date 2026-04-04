from flask import Flask, request, jsonify
import anthropic
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
client = anthropic.Anthropic(api_key=os.environ.get("CLAUDE_API_KEY"))

@app.route("/")
def home():
    return "KFZ Diagnose Server läuft!"

@app.route("/diagnose", methods=["POST"])
def diagnose():
    try:
        data = request.get_json()
        fahrzeug = data.get("fahrzeug", "Unbekanntes Fahrzeug")
        geraeusch = data.get("geraeusch", "Kein Geraeusch erkannt")
        beschreibung = data.get("beschreibung", "")
        sprache = data.get("sprache", "de")

        if sprache == "de":
            prompt = (
                f"Du bist ein erfahrener KFZ-Meister in Deutschland.\n"
                f"Fahrzeug: {fahrzeug}\n"
                f"Erkanntes Geraeusch: {geraeusch}\n"
                f"Zusaetzliche Beschreibung vom Fahrer: {beschreibung}\n\n"
                f"Antworte auf Deutsch, strukturiert:\n"
                f"GERAEUSCH-TYP: (ein kurzer Begriff)\n"
                f"URSACHE: (Top 3 wahrscheinliche Ursachen, jede mit Wahrscheinlichkeit in Prozent, z.B. Querlenker - 70 Prozent, Stossdaempfer - 20 Prozent, Radlager - 10 Prozent)\n"
                f"HAUPTVERDACHT: (das wahrscheinlichste Bauteil mit Prozentzahl, z.B. Querlenker - 70 Prozent wahrscheinlich)\n"
                f"DRINGLICHKEIT: (nur eines: SOFORT / BALD / KANN WARTEN)\n"
                f"KOSTEN: (Spanne in Euro, z.B. 150 - 400 Euro)\n"
                f"ERKLAERUNG: (einfache Erklaerung fuer Laien, 2-3 Saetze. Weise darauf hin dass dies eine KI-Einschaetzung ist und keine 100 Prozent Garantie gegeben werden kann)\n"
                f"MECHANIKER-TIPP: (was genau in der Werkstatt fragen)\n"
                f"WARNUNG: (nur wenn wirklich gefaehrlich, sonst leer lassen)\n\n"
                f"Keine Emojis. Keine Sonderzeichen."
            )
        else:
            prompt = (
                f"You are an experienced car mechanic.\n"
                f"Vehicle: {fahrzeug}\n"
                f"Detected sound: {geraeusch}\n"
                f"Additional description: {beschreibung}\n\n"
                f"Answer in English, structured:\n"
                f"SOUND-TYPE: (short term)\n"
                f"CAUSE: (Top 3 probable causes each with probability in percent, e.g. Control arm - 70 percent, Shock absorber - 20 percent, Wheel bearing - 10 percent)\n"
                f"MAIN-SUSPECT: (most likely part with percentage, e.g. Control arm - 70 percent likely)\n"
                f"URGENCY: (only one: IMMEDIATELY / SOON / CAN WAIT)\n"
                f"COST: (range in local currency)\n"
                f"EXPLANATION: (simple explanation, 2-3 sentences. Note that this is an AI estimate and no 100 percent guarantee can be given)\n"
                f"MECHANIC-TIP: (what exactly to ask at the garage)\n"
                f"WARNING: (only if dangerous, else leave empty)\n\n"
                f"No emojis. No special characters."
            )

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        antwort = message.content[0].text
        logging.info(f"Diagnose erstellt fuer: {fahrzeug}")
        return jsonify({"success": True, "diagnose": antwort})

    except Exception as e:
        logging.error(f"Fehler: {str(e)}")
        return jsonify({"success": False, "fehler": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

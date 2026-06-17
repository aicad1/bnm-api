from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/")
def home():
    return "OK - BNM API is running"

@app.route("/bnm")
def bnm():
    try:
        date = request.args.get("date")
        currency = request.args.get("currency")

        if not date or not currency:
            return jsonify({"error": "missing params"}), 400

        url = f"https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date={date}"

        r = requests.get(url, timeout=10)

        # защита от плохого ответа
        if r.status_code != 200:
            return jsonify({"error": "BNM not available"}), 502

        content = r.text

        # если BNM вернул не XML (часто бывает)
        if "<ValCurs" not in content:
            return jsonify({"error": "invalid response from BNM"}), 502

        root = ET.fromstring(r.content)

        for valute in root.findall(".//Valute"):
            char = valute.find("CharCode")
            value = valute.find("Value")

            if char is not None and value is not None:
                if char.text == currency:
                    return jsonify({
                        "currency": currency,
                        "date": date,
                        "rate": float(value.text.replace(",", "."))
                    })

        return jsonify({"error": "currency not found"}), 404

    except Exception as e:
        return jsonify({
            "error": "server crashed",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run()
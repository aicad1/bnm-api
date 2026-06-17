from flask import Flask, request, jsonify
import requests
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route("/bnm")
def bnm():
    date = request.args.get("date")
    currency = request.args.get("currency")

    if not date or not currency:
        return jsonify({"error": "missing params"}), 400

    url = f"https://www.bnm.md/ru/official_exchange_rates?get_xml=1&date={date}"

    r = requests.get(url, timeout=10)
    r.raise_for_status()

    root = ET.fromstring(r.content)

    for valute in root.findall(".//Valute"):
        if valute.find("CharCode").text == currency:
            value = valute.find("Value").text
            return jsonify({
                "currency": currency,
                "date": date,
                "rate": float(value.replace(",", "."))
            })

    return jsonify({"error": "not found"}), 404


if __name__ == "__main__":
    app.run()
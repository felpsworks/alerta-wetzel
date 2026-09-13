import json

from flask import Flask, jsonify, request, send_from_directory

from db import CHAVES_VALIDAS, get_connection, init_db

app = Flask(__name__, static_folder=None)


@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/<path:nome_arquivo>")
def arquivo_estatico(nome_arquivo):
    # Serve index.html, consulta-pn.html e qualquer outro arquivo estático da
    # raiz do projeto, exatamente como o GitHub Pages faz hoje.
    return send_from_directory(".", nome_arquivo)


@app.route("/api/store/<key>", methods=["GET"])
def api_store_get(key):
    if key not in CHAVES_VALIDAS:
        return jsonify({"erro": f"Chave desconhecida: {key}"}), 404

    conn = get_connection()
    linha = conn.execute("SELECT value FROM kv_store WHERE key = ?", (key,)).fetchone()
    conn.close()

    if linha is None:
        return jsonify({"value": None})
    return jsonify({"value": json.loads(linha["value"])})


@app.route("/api/store/<key>", methods=["PUT"])
def api_store_put(key):
    if key not in CHAVES_VALIDAS:
        return jsonify({"erro": f"Chave desconhecida: {key}"}), 404

    dados = request.get_json(force=True) or {}
    if "value" not in dados:
        return jsonify({"erro": "Corpo precisa ter o campo 'value'."}), 400

    valor_json = json.dumps(dados["value"], ensure_ascii=False)

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO kv_store (key, value, updated_at) VALUES (?, ?, datetime('now', 'localtime'))
        ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at
        """,
        (key, valor_json),
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    # host="0.0.0.0" para ficar acessível por outros computadores na intranet
    # (não só pela própria máquina). Antes de expor de vez na rede da empresa,
    # o TI deve avaliar rodar com debug=False e atrás de um servidor WSGI de
    # produção (ex.: waitress, gunicorn) em vez do servidor de desenvolvimento
    # do Flask.
    app.run(host="0.0.0.0", debug=True, port=5000)

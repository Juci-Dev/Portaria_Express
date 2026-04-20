from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection

morador_bp = Blueprint('morador', __name__, template_folder='../templates')

# Página de cadastro


@morador_bp.route('/')
def cadastro():
  return render_template('cadastro.html', morador=None, mensagem=None)
# Cadastro de morador
@morador_bp.route('/cadastrar', methods=['POST'])
def cadastrar():
    
    nome = request.form.get('nome')
    email = request.form.get('email')
    tel = request.form.get('tel')
    complemento = request.form.get('complemento')

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "INSERT INTO morador (nome, email, tel, complemento) VALUES (%s, %s, %s, %s)",
            (nome, email, tel, complemento)
        )
        conn.commit()
    conn.close()

    flash("Morador cadastrado com sucesso!", "success")
    return redirect(url_for('morador.cadastro'))


# Buscar morador
@morador_bp.route('/buscar', methods=['POST'])
def buscar():
    nome = request.form.get('nome')
    return redirect(url_for('morador.resultado', nome=nome))  # usa blueprint

@morador_bp.route('/resultado')
def resultado():
    nome = request.args.get('nome')

    conn = get_db_connection()
    with conn.cursor(dictionary=True) as cursor:
        cursor.execute("SELECT * FROM morador WHERE nome LIKE %s", (f"%{nome}%",))
        morador = cursor.fetchone()
        cursor.fetchall()

    conn.close()

    if morador:
        return render_template('M_localizado.html', morador=morador)
    else:
        return render_template('M_localizado.html', morador=None, mensagem="Morador não encontrado")

    
    # Atualizar morador
@morador_bp.route('/atualizar', methods=['POST'])
def atualizar():
    id = request.form.get('id')
    nome = request.form.get('nome')
    email = request.form.get('email')
    tel = request.form.get('tel')
    complemento = request.form.get('complemento')

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE morador SET nome=%s, email=%s, tel=%s, complemento=%s WHERE id=%s",
            (nome, email, tel, complemento, id)
        )
        conn.commit()
    conn.close()
    flash("Atualizado com sucesso!", "success")
    return redirect(url_for('morador.cadastro'))

# Excluir morador
@morador_bp.route('/excluir', methods=['POST'])
def excluir():
    id = request.form.get('id')

    conn = get_db_connection()

    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM morador WHERE id = %s", (id,))
        conn.commit()
        print("LINHAS DELETADAS:", cursor.rowcount)

    conn.close()

    return redirect(url_for('morador.cadastro'))




@morador_bp.route('/encomenda/cadastrar/<int:morador_id>', methods=['GET'])
def abrir_encomenda(morador_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM morador WHERE id = %s", (morador_id,))
    morador = cursor.fetchone()

    cursor.execute("""
        SELECT * FROM encomenda
        WHERE morador_id = %s
        ORDER BY id DESC
    """, (morador_id,))
    encomenda = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "encomenda.html",
        morador=morador,
        encomenda=encomenda
    )
@morador_bp.route('/encomenda/cadastrar', methods=['POST'])
def RegistrarEncomenda():

    morador_id = request.form.get('morador_id')
    responsavel = request.form.get('nome_responsavel')
    data_entrada = request.form.get('data_recebimento')
    data_saida = request.form.get('data_entrega')
    status = request.form.get('status')

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO encomenda
        (morador_id, responsavel, data_entrada, data_saida, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (
        morador_id,
        responsavel,
        data_entrada,
        data_saida,
        status
    ))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('morador.abrir_encomenda', morador_id=morador_id))

@morador_bp.route('/encomenda/atualizar', methods=['POST'])
def atualizar_encomenda():

    encomenda_id = request.form.get("encomenda_id")
    status = request.form.get("status")
    data_entrega = request.form.get("data_entrega")

    # 👉 se vier vazio, vira None (NULL no banco)
    if not data_entrega:
        data_entrega = None
        
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE encomenda
        SET status = %s, data_saida = %s
        WHERE id = %s
    """, (status, data_entrega, encomenda_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(request.referrer)

@morador_bp.route('/encomenda/excluir-multiplos', methods=['POST'])
def excluir_multiplos():

    ids = request.form.getlist('ids')

    if not ids:
        return redirect(request.referrer)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM encomenda WHERE id IN (%s)" % ",".join(["%s"] * len(ids)),
        tuple(ids)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(request.referrer)


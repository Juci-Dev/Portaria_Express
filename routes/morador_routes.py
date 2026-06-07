
from flask import Blueprint, render_template, request, flash, url_for, redirect,session
from db import get_db_connection
from urllib.parse import quote
from flask import redirect
import urllib.parse
from datetime import datetime

morador_bp = Blueprint('morador', __name__, template_folder='../templates')

# Página de cadastro

@morador_bp.route('/')
def cadastro():
    
    return redirect(url_for('morador.login'))

#@morador_bp.route('/')
#def cadastro():
  #return render_template('cadastro.html', morador=None, mensagem=None)
@morador_bp.route('/home')
def home():
    return render_template('cadastro.html', morador=None, mensagem=None)
@morador_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('morador.login'))
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

    # morador
    cursor.execute("SELECT * FROM morador WHERE id = %s", (morador_id,))
    morador = cursor.fetchone()

    # encomendas
    cursor.execute("""
        SELECT * FROM encomenda
        WHERE morador_id = %s
        ORDER BY id DESC
    """, (morador_id,))
    encomenda = cursor.fetchall()

    # 🟢 HISTÓRICO WHATSAPP
    cursor.execute("""
        SELECT 
            h.id,
            h.encomenda_id,
            h.morador_id,
            h.mensagem,
            h.data_envio,
            m.nome
        FROM historico_whatsapp h
        INNER JOIN morador m ON m.id = h.morador_id
        WHERE h.morador_id = %s
        ORDER BY h.data_envio DESC
    """, (morador_id,))

    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        "encomenda.html",
        morador=morador,
        encomenda=encomenda,
        historico=historico   # IMPORTANTE
    )
@morador_bp.route('/encomenda/cadastrar', methods=['POST'])
def RegistrarEncomenda():

    morador_id = request.form.get('morador_id')
    responsavel = session.get('usuario')
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

    #  se vier vazio, vira None (NULL no banco)
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

    print("IDS SELECIONADOS:", ids)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM historico_whatsapp WHERE encomenda_id IN (%s)"
        % ",".join(["%s"] * len(ids)),
        tuple(ids)
    )

    print("Históricos apagados:", cursor.rowcount)

    cursor.execute(
        "DELETE FROM encomenda WHERE id IN (%s)"
        % ",".join(["%s"] * len(ids)),
        tuple(ids)
    )

    print("Encomendas apagadas:", cursor.rowcount)

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(request.referrer)



@morador_bp.route('/encomenda/whatsapp/<int:id>')
def enviar_whatsapp_encomenda(id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            m.id AS morador_id,
            m.nome,
            m.tel
        FROM encomenda e
        INNER JOIN morador m
            ON m.id = e.morador_id
        WHERE e.id = %s
    """, (id,))

    dados = cursor.fetchone()

    if not dados:
        cursor.close()
        conn.close()
        return redirect(request.referrer)

    telefone = dados['tel']
    nome = dados['nome']
    morador_id = dados['morador_id']

    mensagem_texto = f"Olá {nome}, sua encomenda chegou na portaria e está disponível para retirada."
    mensagem = quote(mensagem_texto)

    # SALVA HISTÓRICO NO BANCO
    cursor.execute("""
        INSERT INTO historico_whatsapp (encomenda_id, morador_id, mensagem)
        VALUES (%s, %s, %s)
    """, (id, morador_id, mensagem_texto))

    conn.commit()

    cursor.close()
    conn.close()

    # 🔗 redireciona para WhatsApp Web
    return redirect(
        f"https://web.whatsapp.com/send?phone=55{telefone}&text={mensagem}"
    )
    from flask import session

@morador_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        nome = request.form.get('nome')
        senha = request.form.get('senha')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, nome, funcao
            FROM usuario
            WHERE nome = %s AND senha = %s
        """, (nome, senha))

        usuario_portaria = cursor.fetchone()

        cursor.close()
        conn.close()

        if usuario_portaria:

            session['usuario_id'] = usuario_portaria['id']
            session['usuario'] = usuario_portaria['nome']
            session['funcao'] = usuario_portaria['funcao']

            return redirect(url_for('morador.home'))

        return render_template(
            'login.html',
            erro='Usuário ou senha inválidos.'
        )

    return render_template('login.html')


@morador_bp.route('/cadastro_usuario', methods=['GET', 'POST'])
def cadastro_usuario():

    if request.method == 'POST':

        nome = request.form.get('nome')
        senha = request.form.get('senha')
        funcao = request.form.get('funcao')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO usuario (nome, senha, funcao)
            VALUES (%s, %s, %s)
        """, (nome, senha, funcao))

        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('morador.login'))

    return render_template('cadastro_user.html')

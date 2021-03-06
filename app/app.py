from flask import Flask,render_template,jsonify,request,make_response,url_for,redirect
import sqlite3, json
import os

def create_app():
    app = Flask(__name__)
    db_name = 'example.db'

    def calculate_rank(points):
        rank = None
        if points >= 0 and points < 50:
            rank = 3

        if points >= 50 and points < 80:
            rank = 2

        if points >= 80 and points <= 100:
            rank = 1

        return rank

    def get_questoes(codigo_questionario):
        rows = db_query(db_name, "SELECT id, codigo_questionario, enunciado, alternativas FROM questao WHERE codigo_questionario=:codigo_questionario",{"codigo_questionario":codigo_questionario})
        data = []
        for row in rows:
            dict = {
                'id':row[0],
                'codigo_questionario':row[1],
                'enunciado':row[2],
                'alternativas': json.loads(row[3]),
            }
            data.append(dict)
        return data

    def get_questionario(codigo_questionario):
        rows = db_query(db_name, "SELECT * FROM questionario WHERE codigo_questionario = :codigo_questionario;", {"codigo_questionario":codigo_questionario})
        if len(rows) == 0:
            return None

        return {
            'codigo_questionario' : rows[0][0],
            'nome_questionario' : rows[0][1],
            'descricao' : rows[0][2],
            'aberto' : rows[0][3]
        }

    def get_quest_codes():
        quests = db_query(db_name, "SELECT * FROM questionario;")
        list = []
        for row in quests:
            list.append(row[0])
        return list

    def get_resultado(code:str=None):
        command = "SELECT * FROM resultado"
        values = None
        if code is not None:
            command = command + " WHERE codigo_questionario=:codigo_questionario"
            values = {"codigo_questionario" : str(code)}
        command = command + ";"

        try:
            result = []
            rows = db_query(db_name, command, values)
            if len(rows) == 0:
                return None
            else:
                for row in rows:
                    result.append({
                        "id" : row[0],
                        "email" : row[1],
                        "codigo_questionario" : row[2],
                        "gabarito" : json.loads(row[3]),
                        "pontuacao" : row[4],
                    })
        except Exception as e:
            raise e
        return result

    def db_execute(db_name, command, values:dict=None):
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        if values is  None:
            cur.execute(command)
        else:
            cur.execute(command, values)
        con.commit()
        con.close()

    def db_query(db_name, command, values:dict=None):
        result = None
        con = sqlite3.connect('example.db')
        cur = con.cursor()
        if values is  None:
            cur.execute(command)
        else:
            cur.execute(command, values)
        result = cur.fetchall()

        con.close()
        return result

    @app.route('/')
    def page_home():
        return render_template('index.html')

    @app.route('/<code>')
    def page_form(code:str=None):
        if code in get_quest_codes():
            quest = get_questionario(code)
            return render_template(
                'form.html',
                codigo_questionario = quest['codigo_questionario'],
                nome_questionario = quest['nome_questionario'],
                descricao = quest['descricao']
            )

        return "Formul??rio inexistente, volte para tela principal."

    @app.route('/questionario/<code>')
    def api_questionario(code:str=None):
        try:
            quest = get_questoes(code)
        except Exception as e:
            raise e
            quest = {"erro" : "Question??rio n??o existe.", "exception" : e}
        return jsonify(quest)

    @app.route('/resultado', methods = ['POST'])
    def api_create_resultado():
        if request.method == 'POST':
            data = request.json
            if data['questionario'] not in get_quest_codes():
                return {"error":"Question??rio inv??lido."}
            parameters = {
                "email": data['email'],
                "codigo_questionario": str(data['questionario']),
                "gabarito": json.dumps(data['gabarito']),
                "pontuacao": data['pontuacao']
            }
            command = "INSERT INTO resultado (email, codigo_questionario, gabarito, pontuacao) VALUES (:email, :codigo_questionario, :gabarito, :pontuacao)"
            try:
                db_execute(db_name, command, parameters)
                resposta = {"success": "questionario entregue."}
            except Exception as e:
                resposta = {"error":"erro no processamento. "+str(e)}
            return resposta
        return None

    @app.route('/resultado', methods = ['GET'])
    @app.route('/resultado/', methods = ['GET'])
    @app.route('/resultado/<code>', methods = ['GET'])
    def api_resultados(code:str=None):
        try:
            return jsonify(get_resultado(code))
        except Exception as e:
            return {"error": str(e)}

    @app.route('/dashboard')
    @app.route('/dashboard/')
    def page_dashboard_fail():
        return  """
                    <h1>P??gina n??o existe</h1>
                    <br>
                    <a href="/">voltar</a>
                """

    @app.route('/dashboard/<code>')
    def page_dashboard(code:str=None):
        fail_msg = """
                    <h1>P??gina n??o existe</h1>
                    <br>
                    <a href="/">voltar</a>
                """

        if code in get_quest_codes():

            try:
                results = get_resultado(code)
                quest = get_questionario(code)
                count_rank1 = 0
                count_rank2 = 0
                count_rank3 = 0
                for result in results:
                    if calculate_rank(result['pontuacao']) == 1:
                        count_rank1 = count_rank1 + 1
                    if calculate_rank(result['pontuacao']) == 2:
                        count_rank2 = count_rank2 + 1
                    if calculate_rank(result['pontuacao']) == 3:
                        count_rank3 = count_rank2 + 1

                return render_template(
                    'dashboard.html',
                    nome_questionario=quest['nome_questionario'],
                    count_rank1=count_rank1,
                    count_rank2=count_rank2,
                    count_rank3=count_rank3
                )
            except Exception as e:
                fail_msg = """
                            <h1>N??o existem resultados para esse question??rio</h1>
                            <br>
                            <a href="/">voltar</a>
                        """
                return fail_msg


        return fail_msg

    @app.route('/db', methods = ['POST','DELETE'])
    def api_delete_db():
        if request.method == "POST":
            try:
                create_db()
                return jsonify({"msg":"created!"}), 201
            except Exception as e:
                return jsonify({"msg":"error!", "exception":str(e)}), 500

        if request.method == "DELETE":
            try:
                os.remove(db_name)
                return jsonify({"msg":"deleted!"}), 202
            except Exception as e:
                return jsonify({"msg":"error!", "exception":str(e)}), 500

    @app.route('/quest/<quest>', methods = ['POST'])
    def api_load_quest(quest):
        if quest.strip().lower() == "pef_ica_01":
            try:
                return jsonify(pef_ica_01()), 201
            except Exception as e:
                return jsonify({"msg":"error!", "exception":str(e)}), 500
        return jsonify({"msg":"N??o ?? poss??vel inserir esse question??rio."}), 404

    def create_db():
        try:
            db_execute(db_name, """
            CREATE TABLE IF NOT EXISTS resultado (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            codigo_questionario TEXT NOT NULL,
            gabarito TEXT NOT NULL,
            pontuacao INTEGER NOT NULL,
            CONSTRAINT unique_hod UNIQUE (email, codigo_questionario)
            );
            """)

            db_execute(db_name, """
            CREATE TABLE IF NOT EXISTS questionario (
            codigo_questionario TEXT NOT NULL PRIMARY KEY,
            nome_questionario TEXT NOT NULL,
            descricao TEXT NOT NULL,
            aberto INTEGER NOT NULL DEFAULT 0
            );
            """)

            db_execute(db_name, """
            CREATE TABLE IF NOT EXISTS questao (
            id TEXT NOT NULL,
            codigo_questionario TEXT NOT NULL,
            enunciado TEXT NOT NULL,
            alternativas TEXT NOT NULL,
            CONSTRAINT primary_key PRIMARY KEY (id, codigo_questionario)
            );
            """)

            return {"msg":"done!"}
        except Exception as e:
            return {"msg":"error!", "exception":str(e)}

    def pef_ica_01():
        try:
            #questionario 1
            db_execute(db_name, """
                INSERT INTO questionario (codigo_questionario, nome_questionario, descricao, aberto) VALUES (:codigo_questionario, :nome_questionario, :descricao, :aberto);
            """, {
                "codigo_questionario" : "PEF_ICA_01",
                "nome_questionario" : "Teste de Diagn??stico Financeiro",
                "descricao" : "O presente teste tem por finalidade diagnosticar a sa??de financeira do nosso efetivo, para que a equipe do Programa de Educa????o Financeira possa utilizar os dados obtidos na cria????o de conte??dos.",
                "aberto" : 1,
            })

            # q1
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q1",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "O que voc?? ganha por m??s ?? suficiente para arcar com os seus gastos?",
                "alternativas" : json.dumps([
                        {"id" : "a",
                            "text": "Consigo pagar as minhas contas e ainda sobra dinheiro para guardar;",
                            "points": 10,
                        },
                        {"id" : "b",
                            "text": "?? suficiente, mas n??o sobra nada;",
                            "points": 5,
                        },
                        {"id" : "c",
                            "text": "Gasto todo o meu dinheiro e ainda uso o limite do cheque especial ou pe??o emprestado para parentes e amigos.",
                            "points": 0,
                        },
                    ]),
            })

            # q2
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q2",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Voc?? tem conseguido pagar as suas despesas em dia e ?? vista?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Pago em dia, ?? vista e, em alguns casos, com bons descontos;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Quase sempre, mas tenho que parcelar as compras de maior valor;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "Sempre parcelo os meus compromissos e utilizo linhas de cr??dito como cheque especial, cart??o de cr??dito e credi??rio.",
                        "points": 0,
                    },
                ]),
            })

            # q3
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q3",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Voc?? monta o seu or??amento financeiro mensalmente?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Fa??o periodicamente e comparo o or??ado com o realizado;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Somente registro o realizado, sem analisar os gastos;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "N??o fa??o o meu or??amento financeiro.",
                        "points": 0,
                    },
                ]),
            })

            # q4
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q4",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Voc?? consegue fazer algum tipo de investimento?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Utilizo mais de 10% da minha renda mensal em linhas de investimento que variam de acordo com os meus objetivos;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Quando sobra dinheiro, invisto, normalmente, na poupan??a;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "Nunca sobra dinheiro para investir.",
                        "points": 0,
                    },
                ]),
            })

            # q5
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q5",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Como voc?? planeja a sua aposentadoria?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Contribuo ou n??o para um Sistema de Prote????o Social e tenho planos alternativos por meio de investimentos em geral;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Contribuo ou n??o para um Sistema de Prote????o Social, mas n??o consigo poupar adequadamente para realizar planos alternativos nesse sentido;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "Contribuo ou n??o para um Sistema de Prote????o Social e n??o tenho ideia alguma de como realizar planos alternativos nesse sentido.",
                        "points": 0,
                    },
                ]),
            })

            # q6
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q6",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "O que voc?? entende sobre ser Independente Financeiramente?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Que posso trabalhar por prazer e n??o por necessidade;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Que posso ter dinheiro para viver bem o dia a dia;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "Que posso aproveitar a vida intensamente e n??o pensar no futuro.",
                        "points": 0,
                    },
                ]),
            })

            # q7
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q7",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Voc?? sabe quais s??o os seus sonhos e objetivos de curto, m??dio e longo prazo?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Sei quais s??o, quanto custam e por quanto tempo terei que guardar para realiz??-los;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Tenho muitos e sei quanto custam, mas n??o sei como realiz??-los;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "N??o tenho ou, se tenho, sempre acabo deixando-os para o futuro, porque n??o consigo guardar dinheiro para eles.",
                        "points": 0,
                    },
                ]),
            })

            # q8
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q8",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Se um imprevisto alterasse a sua situa????o financeira, qual seria a sua rea????o?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Faria um bom diagn??stico financeiro, registrando o que ganho e o que gasto, al??m dos meus investimentos e d??vidas, se os tiverem;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Cortaria despesas e gastos desnecess??rios;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "N??o saberia por onde come??ar e teria medo de encarar a minha verdadeira situa????o financeira.",
                        "points": 0,
                    },
                ]),
            })

            # q9
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q9",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Se a partir de hoje voc?? n??o recebesse mais a sua renda mensal, por quanto tempo voc?? conseguiria manter seu atual padr??o de vida?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Conseguiria fazer tudo que fa??o por 5, 10 ou mais anos;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Manteria meu padr??o de vida por 1 a, no m??ximo, 4 anos;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "N??o conseguiria me manter nem por alguns meses.",
                        "points": 0,
                    },
                ]),
            })

            # q10
            db_execute(db_name, """
                INSERT INTO questao (id, codigo_questionario, enunciado, alternativas) VALUES (:id, :codigo_questionario, :enunciado, :alternativas);
            """, {
                "id" : "q10",
                "codigo_questionario" : "PEF_ICA_01",
                "enunciado" : "Quando voc?? decide comprar um produto, qual ?? a sua atitude?",
                "alternativas" : json.dumps([
                    {"id" : "a",
                        "text": "Planejo uma forma de investimento para comprar ?? vista e com desconto;",
                        "points": 10,
                    },
                    {"id" : "b",
                        "text": "Parcelo dentro do meu or??amento;",
                        "points": 5,
                    },
                    {"id" : "c",
                        "text": "Compro e depois me preocupo como vou pagar.",
                        "points": 0,
                    },
                ]),
            })

            return {"msg":"PEF_ICA_01 done!"}
        except Exception as e:
            raise e


    return app

if __name__ == '__main__':
    create_app().run(debug=False, host='0.0.0.0')

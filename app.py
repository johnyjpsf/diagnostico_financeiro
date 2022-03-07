from flask import Flask,render_template,jsonify,request,make_response,url_for,redirect
import sqlite3, json

app = Flask(__name__)
db_name = 'example.db'

def get_questionarios():
    questionarios = {}
    questionarios['PEF_ICA_01'] = [
        {"id": "q1",
            "question": "O que você ganha por mês é suficiente para arcar com os seus gastos?",
            "alternatives": [
                {"id" : "a",
                    "text": "Consigo pagar as minhas contas e ainda sobra dinheiro para guardar;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "É suficiente, mas não sobra nada;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Gasto todo o meu dinheiro e ainda uso o limite do cheque especial ou peço emprestado para parentes e amigos.",
                    "points": 0,
                },
            ],
        },
        {"id": "q2",
            "question": "Você tem conseguido pagar as suas despesas em dia e à vista?",
            "alternatives": [
                {"id" : "a",
                    "text": "Pago em dia, à vista e, em alguns casos, com bons descontos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Quase sempre, mas tenho que parcelar as compras de maior valor;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Sempre parcelo os meus compromissos e utilizo linhas de crédito como cheque especial, cartão de crédito e crediário.",
                    "points": 0,
                },
            ],
        },
        {"id": "q3",
            "question": "Você monta o seu orçamento financeiro mensalmente?",
            "alternatives": [
                {"id" : "a",
                    "text": "Faço periodicamente e comparo o orçado com o realizado;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Somente registro o realizado, sem analisar os gastos;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não faço o meu orçamento financeiro.",
                    "points": 0,
                },
            ],
        },
        {"id": "q4",
            "question": "Você consegue fazer algum tipo de investimento?",
            "alternatives": [
                {"id" : "a",
                    "text": "Utilizo mais de 10% da minha renda mensal em linhas de investimento que variam de acordo com os meus objetivos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Quando sobra dinheiro, invisto, normalmente, na poupança;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Nunca sobra dinheiro para investir.",
                    "points": 0,
                },
            ],
        },
        {"id": "q5",
            "question": "Como você planeja a sua aposentadoria?",
            "alternatives": [
                {"id" : "a",
                    "text": "Contribuo ou não para um Sistema de Proteção Social e tenho planos alternativos por meio de investimentos em geral;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Contribuo ou não para um Sistema de Proteção Social, mas não consigo poupar adequadamente para realizar planos alternativos nesse sentido;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Contribuo ou não para um Sistema de Proteção Social e não tenho ideia alguma de como realizar planos alternativos nesse sentido.",
                    "points": 0,
                },
            ],
        },
        {"id": "q6",
            "question": "O que você entende sobre ser Independente Financeiramente?",
            "alternatives": [
                {"id" : "a",
                    "text": "Que posso trabalhar por prazer e não por necessidade;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Que posso ter dinheiro para viver bem o dia a dia;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Que posso aproveitar a vida intensamente e não pensar no futuro.",
                    "points": 0,
                },
            ],
        },
        {"id": "q7",
            "question": "Você sabe quais são os seus sonhos e objetivos de curto, médio e longo prazo?",
            "alternatives": [
                {"id" : "a",
                    "text": "Sei quais são, quanto custam e por quanto tempo terei que guardar para realizá-los;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Tenho muitos e sei quanto custam, mas não sei como realizá-los;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não tenho ou, se tenho, sempre acabo deixando-os para o futuro, porque não consigo guardar dinheiro para eles.",
                    "points": 0,
                },
            ],
        },
        {"id": "q8",
            "question": "Se um imprevisto alterasse a sua situação financeira, qual seria a sua reação?",
            "alternatives": [
                {"id" : "a",
                    "text": "Faria um bom diagnóstico financeiro, registrando o que ganho e o que gasto, além dos meus investimentos e dívidas, se os tiverem;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Cortaria despesas e gastos desnecessários;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não saberia por onde começar e teria medo de encarar a minha verdadeira situação financeira.",
                    "points": 0,
                },
            ],
        },
        {"id": "q9",
            "question": "Se a partir de hoje você não recebesse mais a sua renda mensal, por quanto tempo você conseguiria manter seu atual padrão de vida?",
            "alternatives": [
                {"id" : "a",
                    "text": "Conseguiria fazer tudo que faço por 5, 10 ou mais anos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Manteria meu padrão de vida por 1 a, no máximo, 4 anos;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não conseguiria me manter nem por alguns meses.",
                    "points": 0,
                },
            ],
        },
        {"id": "q10",
            "question": "Quando você decide comprar um produto, qual é a sua atitude?",
            "alternatives": [
                {"id" : "a",
                    "text": "Planejo uma forma de investimento para comprar à vista e com desconto;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Parcelo dentro do meu orçamento;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Compro e depois me preocupo como vou pagar.",
                    "points": 0,
                },
            ],
        },
    ];
    return questionarios

def get_quest_codes():
    return get_questionarios().keys()

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
def home():
    return render_template('index.html')

@app.route('/<code>')
def form(code:str=None):
    if code in get_quest_codes():
        return render_template('form.html', code=code)

    return "formulário inexistente, volte para tela principal."

@app.route('/questionario/<code>')
def get_questionario(code:str=None):
    questionarios = {}
    questionarios['PEF_ICA_01'] = [
        {"id": "q1",
            "question": "O que você ganha por mês é suficiente para arcar com os seus gastos?",
            "alternatives": [
                {"id" : "a",
                    "text": "Consigo pagar as minhas contas e ainda sobra dinheiro para guardar;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "É suficiente, mas não sobra nada;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Gasto todo o meu dinheiro e ainda uso o limite do cheque especial ou peço emprestado para parentes e amigos.",
                    "points": 0,
                },
            ],
        },
        {"id": "q2",
            "question": "Você tem conseguido pagar as suas despesas em dia e à vista?",
            "alternatives": [
                {"id" : "a",
                    "text": "Pago em dia, à vista e, em alguns casos, com bons descontos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Quase sempre, mas tenho que parcelar as compras de maior valor;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Sempre parcelo os meus compromissos e utilizo linhas de crédito como cheque especial, cartão de crédito e crediário.",
                    "points": 0,
                },
            ],
        },
        {"id": "q3",
            "question": "Você monta o seu orçamento financeiro mensalmente?",
            "alternatives": [
                {"id" : "a",
                    "text": "Faço periodicamente e comparo o orçado com o realizado;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Somente registro o realizado, sem analisar os gastos;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não faço o meu orçamento financeiro.",
                    "points": 0,
                },
            ],
        },
        {"id": "q4",
            "question": "Você consegue fazer algum tipo de investimento?",
            "alternatives": [
                {"id" : "a",
                    "text": "Utilizo mais de 10% da minha renda mensal em linhas de investimento que variam de acordo com os meus objetivos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Quando sobra dinheiro, invisto, normalmente, na poupança;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Nunca sobra dinheiro para investir.",
                    "points": 0,
                },
            ],
        },
        {"id": "q5",
            "question": "Como você planeja a sua aposentadoria?",
            "alternatives": [
                {"id" : "a",
                    "text": "Contribuo ou não para um Sistema de Proteção Social e tenho planos alternativos por meio de investimentos em geral;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Contribuo ou não para um Sistema de Proteção Social, mas não consigo poupar adequadamente para realizar planos alternativos nesse sentido;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Contribuo ou não para um Sistema de Proteção Social e não tenho ideia alguma de como realizar planos alternativos nesse sentido.",
                    "points": 0,
                },
            ],
        },
        {"id": "q6",
            "question": "O que você entende sobre ser Independente Financeiramente?",
            "alternatives": [
                {"id" : "a",
                    "text": "Que posso trabalhar por prazer e não por necessidade;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Que posso ter dinheiro para viver bem o dia a dia;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Que posso aproveitar a vida intensamente e não pensar no futuro.",
                    "points": 0,
                },
            ],
        },
        {"id": "q7",
            "question": "Você sabe quais são os seus sonhos e objetivos de curto, médio e longo prazo?",
            "alternatives": [
                {"id" : "a",
                    "text": "Sei quais são, quanto custam e por quanto tempo terei que guardar para realizá-los;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Tenho muitos e sei quanto custam, mas não sei como realizá-los;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não tenho ou, se tenho, sempre acabo deixando-os para o futuro, porque não consigo guardar dinheiro para eles.",
                    "points": 0,
                },
            ],
        },
        {"id": "q8",
            "question": "Se um imprevisto alterasse a sua situação financeira, qual seria a sua reação?",
            "alternatives": [
                {"id" : "a",
                    "text": "Faria um bom diagnóstico financeiro, registrando o que ganho e o que gasto, além dos meus investimentos e dívidas, se os tiverem;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Cortaria despesas e gastos desnecessários;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não saberia por onde começar e teria medo de encarar a minha verdadeira situação financeira.",
                    "points": 0,
                },
            ],
        },
        {"id": "q9",
            "question": "Se a partir de hoje você não recebesse mais a sua renda mensal, por quanto tempo você conseguiria manter seu atual padrão de vida?",
            "alternatives": [
                {"id" : "a",
                    "text": "Conseguiria fazer tudo que faço por 5, 10 ou mais anos;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Manteria meu padrão de vida por 1 a, no máximo, 4 anos;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Não conseguiria me manter nem por alguns meses.",
                    "points": 0,
                },
            ],
        },
        {"id": "q10",
            "question": "Quando você decide comprar um produto, qual é a sua atitude?",
            "alternatives": [
                {"id" : "a",
                    "text": "Planejo uma forma de investimento para comprar à vista e com desconto;",
                    "points": 10,
                },
                {"id" : "b",
                    "text": "Parcelo dentro do meu orçamento;",
                    "points": 5,
                },
                {"id" : "c",
                    "text": "Compro e depois me preocupo como vou pagar.",
                    "points": 0,
                },
            ],
        },
    ];

    try:
        quest = questionarios[code]
    except Exception as e:
        quest = {"erro" : "Questionário não existe."}

    return jsonify(quest)

@app.route('/resultado', methods = ['GET'])
@app.route('/resultado/', methods = ['GET'])
@app.route('/resultado/<code>', methods = ['GET'])
def get_resultados(code=None):
    command = "SELECT * FROM resultado"
    values = None
    if code is not None:
        command = command + " WHERE pesquisa=:pesquisa"
        values = {"pesquisa" : str(code)}
    command = command + ";"

    result = None
    try:
        result = []
        for row in db_query(db_name, command, values):
            new_row = {
                "id" : row[0],
                "email" : row[1],
                "pesquisa" : row[2],
                "gabarito" : json.loads(row[3]),
                "pontuacao" : row[4],
            }
            result.append(new_row)
    except Exception as e:
        raise e
        result = {"erro" : str(e)}

    return jsonify(result)

@app.route('/resultado', methods = ['POST'])
def create_resultado():
    if request.method == 'POST':
        data = request.json
        if data['pesquisa'] not in get_quest_codes():
            return "Qustionário inválido."

        parameters = {
            "email": data['email'],
            "pesquisa": str(data['pesquisa']),
            "gabarito": str(data['gabarito']),
            "pontuacao": data['pontuacao']
        }

        command = "INSERT INTO resultado (email, pesquisa, gabarito, pontuacao) VALUES (:email, :pesquisa, :gabarito, :pontuacao)"
        try:
            db_execute(db_name, command, parameters)
            resposta = "pesquisa entregue."
        except Exception as e:
            resposta = "erro no processamento."
            print("\n",e,"\n")
            # raise e

        return resposta

    return None


if __name__ == '__main__':
    db_execute(db_name, """
        CREATE TABLE IF NOT EXISTS resultado (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            pesquisa TEXT NOT NULL,
            gabarito TEXT NOT NULL,
            pontuacao INTEGER NOT NULL
        );
    """)
    app.run(debug=True)

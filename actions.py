# API IBGE: https://servicodados.ibge.gov.br/api/docs/localidades?versao=1
# API https://viacep.com.br/ws/{CEP}/json/

from typing import Any, Text, Dict, List, Union, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

# importação do form
from rasa_sdk.forms import FormAction

# para requisições a api
import requests

# expressão regular para validar nome -> Regular Expression
import re

# para manuseio de arquivos json
# import json

# para lidar com data
from datetime import date


# FORM TO TAKE PACIENT'S BASICS INFORMATIONS
class DadosForm(FormAction):
    """ Início do formulário """
    def name(self) -> Text:
        """ Nome único do formulário """
        return "dados_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """ List de todos os slots que deverão ser preenchidos """
        return ["nome", "nascimento", "cep", "sexo", "escolaridade", "profissao", "vinha_bem_ate_quando"]
        # return ["nome"]
        

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """ Um dicionário para mapear todos os slots necessário para:
        - extrair entidades
        - intenções
        - mensagem inteira
        ou uma lista de item"""

        return{
            "nome":[
                self.from_entity(entity="nome"),
                self.from_text()
            ],
            "nascimento":[
                self.from_entity(entity="nascimento"), 
                self.from_text()
            ],
            "cep":[
                self.from_entity(entity="cep"), 
                self.from_text()
            ],
            "sexo":[
                self.from_entity(entity="sexo"), 
                self.from_text(intent="sexo")
            ],
            "escolaridade":[
                self.from_entity(entity="escolaridade"), 
                self.from_text(intent="escolaridade")
            ],
            "profissao":[
                self.from_entity(entity="profissao"), 
                self.from_text(intent="profissao")
            ],
            "vinha_bem_ate_quando": [
                self.from_entity(entity="vinha_bem_ate_quando"),
                self.from_text()
            ]
        }

    
    def validate_nome(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando nome usando expressão regular """

        # conter apenas de A a Z, excluindo caracteres especiais e números
        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"nome":value}
        else:
            dispatcher.utter_message("Não consegui verificar corretamente")
            return {"nome": None}


    def validate_sexo(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando sexo """

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"sexo":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Não entendi. Por gentileza, digite de novo")
            return {"sexo": None}


    def validate_nascimento(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validação da data de nascimento """

        data = value
        # dia_atual = date.today().day
        # mes_atual = date.today().month
        ano_atual = date.today().year

        try:
            # faz o split e transforma em números. Mapeia a string recebida, quebra na barra e transforma pra int
            dia, mes, ano = map(int, data.split('/'))

            # mes ou ano inválido, retorna False
            if mes < 1 or mes > 12 or ano <= 1900 or ano >= ano_atual:
                dispatcher.utter_message("Não consegui verificar a data")
                return {"nascimento" : None}

            # verifica qual o último dia do mês:
            if mes in (1, 3, 5, 7, 8, 10, 12):
                ultimo_dia = 31

            # verifica mês de fevereiro. Inclusive se é bissexto:
            elif mes == 2:
                if (ano % 4 == 0) and (ano % 100 != 0 or ano % 400 == 0):
                    ultimo_dia = 29
                else:
                    ultimo_dia = 28

            else:
                ultimo_dia = 30

            # verifica se o dia é válido
            if dia < 1 or dia > ultimo_dia:
                dispatcher.utter_message("Não consegui verificar a data")
                return {"nascimento" : None}

            # todas as verificações feitas, data de nascimento recebe valor inserido do usuário e calcula idade:
            idade = ano_atual - ano
            return {"nascimento":value, "idade" : idade}

        except ValueError:
            dispatcher.utter_message("Não consegui verificar a data")
            return {"nascimento" : None}


    def validate_cep(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validação do CEP e verificação do mesmo chamando API """

        # substituir ponto, e traço respectivamente
        cep = value.replace('.', '')
        new_cep = cep.replace('-', '')

        # verificar se o valor contém 8 dígitos
        if len(new_cep) == 8:
            # conectando na API passando o CEP
            address = requests.get("https://viacep.com.br/ws/" + new_cep + "/json/").json()

            # se for inválido, printar mensagem de erro pedindo CEP novamente
            if address == {'erro': True}:
                dispatcher.utter_message("CEP inválido ou não encontrado. Deve conter apenas 8 dígitos numéricos")
                return {"cep": None}

            # se for válido, printa endereço
            else:
                # pegar valor do endereco
                endereco = tracker.get_slot("endereco")

                # endereço recebe o valor vindo da chamada da API
                endereco = address['logradouro']
                bairro = address['bairro']
                localidade = address['localidade']
                uf = address['uf']
                endereco_completo = "{}, {}, {} - {}.".format(endereco, bairro, localidade, uf)
                # dispatcher.utter_message(endereco_completo)
                return {"cep": value, "endereco": endereco_completo}
        
        # printar erro se não tiver 8 dígitos
        else:
            dispatcher.utter_message("CEP inválido ou não encontrado. Deve conter apenas 8 dígitos numéricos")
            return {"cep": None}


    def validate_escolaridade(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando escolaridade """ 

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"escolaridade":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"escolaridade": None}


    def validate_profissao(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando profissão """ 

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"profissao":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"profissao": None}


    def validate_vinha_bem_ate_quando(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando vinha_bem_ate_quando """ 

        if (value != None):
            return {"vinha_bem_ate_quando":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"vinha_bem_ate_quando": None}


    # def validate_vinha_bem_ate_quando(self,
    #     value: Text,
    #     dispatcher: CollectingDispatcher,
    #     tracker: Tracker,
    #     domain: Dict[Text, Any],
    #     ) -> Dict[Text, Any]:
    #     """ Validação para extrair data - 'vinha bem até quanto' """

    #     # date_input = value
    #     tempo = tracker.get_slot("tempo")
    #     dia = tracker.get_slot("dia")
    #     user_input = value
    #     dia = date.today().day
    #     mes = date.today().month
    #     ano = date.today().year

    #     if (tempo == "hoje" or tempo == "hj"):
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (tempo == "agora" or tempo == "a noite" or tempo == "à noite" or tempo == "de noite" or tempo == "a tarde" or tempo == "à tarde" or tempo == "de tarde" or tempo == "de manhã" or tempo == "pela manha" or tempo == "manha" or tempo == "manhã"):
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (tempo == "ontem" or tempo == "onti" or tempo == "ante ontem" or tempo == "antes de ontem"):
    #         dia -= 1
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (dia == "domingo" or dia == "segunda" or dia == "terça" or dia == "terca" or dia == "quarta" or dia == "quinta" or dia == "sexta" or dia == "sabado" or dia == "sábado"):
    #         dia -= 7
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (tempo == "semana" or tempo == "semana passada" or tempo == "semanas"):
    #         dia -= 7
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (tempo == "mes" or tempo == "mês" or tempo == "mes passado" or tempo == "mês passado" or tempo == "meses"):
    #         mes -= 1
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     elif (tempo == "ano" or tempo == "ano passado" or tempo == "anos"):
    #         ano -= 1
    #         data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
    #         return{"vinha_bem_ate_quando":data_extraida}

    #     else:
    #         data_extraida = "paciente disse: '{}', não consegui estipular data aproximada.".format(user_input)
    #         return{"vinha_bem_ate_quando":data_extraida}


    def submit(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        """ Depois de ter coletado todos os slots, fazer o submit """

        # coletando dados e salvando em variáveis
        nome = tracker.get_slot("nome")
        nascimento = tracker.get_slot("nascimento")
        idade = tracker.get_slot("idade")
        cep = tracker.get_slot("cep")
        endereco_completo = tracker.get_slot("endereco")
        sexo = tracker.get_slot("sexo")
        escolaridade = tracker.get_slot("escolaridade")
        profissao = tracker.get_slot("profissao")
        vinha_bem_ate_quando = tracker.get_slot("vinha_bem_ate_quando")
        # time = tracker.get_slot("time")

        # printar mensagem de sucesso  
        dispatcher.utter_message("Ok! Confirmando seus dados: \nNome: {} \nData de nascimento: {} \nIdade: {} anos \nCEP: {} \nEndereço: {} \nSexo: {} \nEscolaridade: {} \nProfissão: {} \nVinha bem até: {} \nOk.".format(nome, nascimento, idade, cep, endereco_completo, sexo, escolaridade, profissao, vinha_bem_ate_quando))
        # dispatcher.utter_message("Ok! Confirmando seus dados: \nNome: {} \nVinha bem até: {}.".format(nome, time))
        
        return []




# FORM TO ANALYSE FEVER
# class FebreForm(FormAction):
#     """ Início do formulário """
#     def name(self) -> Text:
#         """ Nome único do formulário """
#         return "febre_form"

#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#         """ List de todos os slots que deverão ser preenchidos """
#         # return ["vinha_bem_ate_quando", "o_que_aconteceu", "o_que_aconteceu_depois", "quando_foi_isso"]
#         return ["temperature", "duracao", "sintomas", "o_que_aconteceu_depois", "quando_foi_isso"]

#     def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
#         """ Um dicionário para mapear todos os slots necessário para:
#         - extrair entidades
#         - intenções
#         - mensagem inteira
#         ou uma lista de item,  """

#         return{            
#             "temperature":[
#                 self.from_entity(entity="temperature"),
#                 self.from_text()
#             ],
#             "duracao":[
#                 self.from_entity(entity="duracao"),
#                 self.from_text()
#             ],
#             "sintomas":[
#                 self.from_entity(entity="sintomas"),
#                 self.from_text()
#             ],
#             "o_que_aconteceu_depois":[
#                 self.from_entity(entity="o_que_aconteceu_depois"),
#                 self.from_text()
#             ],
#             "quando_foi_isso":[
#                 self.from_entity(entity="quando_foi_isso"),
#                 self.from_text()
#             ]
#         }


#     def validate_temperature(self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> Dict[Text, Any]:
#         """ Validando graus da febre """
        
#         # if value.isdigit() and float(value) > 1:
#         if (value != None):
#             return {"temperature": value}
#             # if float(value) <= 37.5:
#             #     return {"temperature": "Classificação - leve: {} °C".format(value)}
#             # if float(value) >= 37.6 and float(value) <= 38.5:
#             #     return {"temperature": "Classificação - moderada: {} °C".format(value)}
#             # else:
#             #     return {"temperature": "Classificação - alta: {} °C".format(value)}
#         else:
#             dispatcher.utter_message("Não entendi.")
#             return {"temperature": None}


#     def validate_duracao(self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> Dict[Text, Any]:

#         duracao = int(value)
#         if duracao <= 0:
#             dispatcher.utter_message("Número de dias inválido")
#             return{"duracao": None}
#         elif duracao <= 7:
#             return{"duracao": "Recente (menos de 7 dias)"}
#         else:
#             return{"duracao": "Prolongada (mais de 7 dias)"}


#     def validate_sintomas(self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> Dict[Text, Any]:
#         """ validando sintomas """

#         if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
#             return {"sintomas":value}
#         else:
#             # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
#             dispatcher.utter_message("Não entendi.")
#             return {"sintomas": None}


#     def validate_o_que_aconteceu_depois(self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> Dict[Text, Any]:
#         """ Validando sintoma - o que aconteceu depois """ 

#         if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
#             return {"o_que_aconteceu_depois":value}
#         else:
#             # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
#             dispatcher.utter_message("Acho que não entendi")
#             return {"o_que_aconteceu_depois": None}



#     def validate_quando_foi_isso(self,
#         value: Text,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> Dict[Text, Any]:
#         """ Validação para extrair data - 'quando foi isso' """

#         if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
#             return {"quando_foi_isso":value}
#         else:
#             # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
#             dispatcher.utter_message("Acho que não entendi")
#             return {"quando_foi_isso": None}

#         # # date_input = value
#         # tempo = tracker.get_slot("tempo")
#         # dia_extraido = tracker.get_slot("dia")
#         # user_input = value
#         # dia = date.today().day
#         # mes = date.today().month
#         # ano = date.today().year

#         # if (tempo == "hoje" or tempo == "hj"):
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (tempo == "agora" or tempo == "a noite" or tempo == "à noite" or tempo == "de noite" or tempo == "a tarde" or tempo == "à tarde" or tempo == "de tarde" or tempo == "de manhã" or tempo == "pela manha" or tempo == "manha" or tempo == "manhã"):
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (tempo == "ontem" or tempo == "onti" or tempo == "ante ontem" or tempo == "antes de ontem"):
#         #     dia -= 1
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (dia_extraido == "domingo" or dia_extraido == "segunda" or dia_extraido == "terça" or dia_extraido == "terca" or dia_extraido == "quarta" or dia_extraido == "quinta" or dia_extraido == "sexta" or dia_extraido == "sabado" or dia_extraido == "sábado"):
#         #     dia -= 7
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (tempo == "semana" or tempo == "semana passada" or tempo == "semanas"):
#         #     dia -= 7
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (tempo == "mes" or tempo == "mês" or tempo == "mes passado" or tempo == "mês passado" or tempo == "meses"):
#         #     mes -= 1
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # if (tempo == "ano" or tempo == "ano passado" or tempo == "anos"):
#         #     ano -= 1
#         #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
#         #     return{"quando_foi_isso":data_extraida}

#         # else:
#         #     data_extraida = "paciente disse: '{}', não consegui estipular data aproximada.".format(user_input)
#         #     return{"quando_foi_isso":data_extraida}




#     def submit(self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#         ) -> List[Dict]:
#         """ Depois de ter coletado todos os slots, fazer o submit """

#         # coletando dados e salvando em variáveis

#         temperature = tracker.get_slot("temperature")
#         duracao = tracker.get_slot("duracao")
#         sintomas = tracker.get_slot("sintomas")

#         o_que_aconteceu_depois = tracker.get_slot("o_que_aconteceu_depois")
#         quando_foi_isso = tracker.get_slot("quando_foi_isso")

#         # printar mensagem de sucesso  
#         #dispatcher.utter_message("Certo {}! Confirmando sua queixa:\n\n Vinha bem até: {}\n O que aconteceu: {}\n Aconteceu depois: {}\n Quando foi isso: {} \n \n Ok, tudo certo! Vou repassar as informações ao médico para continuarmos sua consulta. Obrigado e até logo.".format(nome, vinha_bem_ate_quando, o_que_aconteceu, o_que_aconteceu_depois, quando_foi_isso))
#         dispatcher.utter_message("Certo! Confirmando queixa da febre: \nTemperatura: {} \nDuração: {} \nSente sintomas descritos? {} \nAconteceu depois: {} \nQuando foi isso: {} \nOk, tudo certo! Vou repassar as informações ao médico para continuarmos sua consulta.".format(temperature, duracao, sintomas, o_que_aconteceu_depois, quando_foi_isso))
        
#         return []




# FORM TO ANALYSE PAIN
class DorForm(FormAction):
    """ Início do formulário """
    def name(self) -> Text:
        """ Nome único do formulário """
        return "dor_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """ List de todos os slots que deverão ser preenchidos """
        return ["onde_doi_exatamente", "duracao_da_dor", "o_que_aconteceu_depois", "quando_foi_isso"]
        # return ["time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """ Um dicionário para mapear todos os slots necessário para:
        - extrair entidades
        - intenções
        - mensagem inteira
        ou uma lista de item,  """

        return{            
            "onde_doi_exatamente":[
                self.from_entity(entity="onde_doi_exatamente"),
                self.from_text()
            ],
            "duracao_da_dor":[
                self.from_entity(entity="duracao_da_dor"),
                self.from_text()
            ],
            "o_que_aconteceu_depois":[
                self.from_entity(entity="o_que_aconteceu_depois"),
                self.from_text()
            ],
            "quando_foi_isso":[
                self.from_entity(entity="quando_foi_isso"),
                self.from_text()
            ]
        }


    def validate_onde_doi_exatamente(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando graus da febre """
        
        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"onde_doi_exatamente":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"onde_doi_exatamente": None}


    def validate_duracao_da_dor(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"duracao_da_dor":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"duracao_da_dor": None}


    def validate_o_que_aconteceu_depois(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando sintoma - o que aconteceu depois """ 

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"o_que_aconteceu_depois":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"o_que_aconteceu_depois": None}



    def validate_quando_foi_isso(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validação para extrair data - 'quando foi isso' """

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"quando_foi_isso":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"quando_foi_isso": None}

        # # date_input = value
        # tempo = tracker.get_slot("tempo")
        # dia_extraido = tracker.get_slot("dia")
        # user_input = value
        # dia = date.today().day
        # mes = date.today().month
        # ano = date.today().year

        # if (tempo == "hoje" or tempo == "hj"):
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "agora" or tempo == "a noite" or tempo == "à noite" or tempo == "de noite" or tempo == "a tarde" or tempo == "à tarde" or tempo == "de tarde" or tempo == "de manhã" or tempo == "pela manha" or tempo == "manha" or tempo == "manhã"):
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "ontem" or tempo == "onti" or tempo == "ante ontem" or tempo == "antes de ontem"):
        #     dia -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (dia_extraido == "domingo" or dia_extraido == "segunda" or dia_extraido == "terça" or dia_extraido == "terca" or dia_extraido == "quarta" or dia_extraido == "quinta" or dia_extraido == "sexta" or dia_extraido == "sabado" or dia_extraido == "sábado"):
        #     dia -= 7
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "semana" or tempo == "semana passada" or tempo == "semanas"):
        #     dia -= 7
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "mes" or tempo == "mês" or tempo == "mes passado" or tempo == "mês passado" or tempo == "meses"):
        #     mes -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "ano" or tempo == "ano passado" or tempo == "anos"):
        #     ano -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # else:
        #     data_extraida = "paciente disse: '{}', não consegui estipular data aproximada.".format(user_input)
        #     return{"quando_foi_isso":data_extraida}


    def submit(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        """ Depois de ter coletado todos os slots, fazer o submit """

        # coletando dados e salvando em variáveis

        onde_doi_exatamente = tracker.get_slot("onde_doi_exatamente")
        duracao_da_dor = tracker.get_slot("duracao_da_dor")
        o_que_aconteceu_depois = tracker.get_slot("o_que_aconteceu_depois")
        quando_foi_isso = tracker.get_slot("quando_foi_isso")
        # time = tracker.get_slot("time")

        # printar mensagem de sucesso  
        dispatcher.utter_message("Certo! Confirmando queixa da dor: \nOnde doi: {} \nDuração da dor: {} \nAconteceu depois: {} \nQuando foi isso: {} \nOk, tudo certo! Vou repassar as informações ao médico para continuarmos sua consulta.".format(onde_doi_exatamente, duracao_da_dor, o_que_aconteceu_depois, quando_foi_isso))
        # dispatcher.utter_message("DATE EXTRACTED: {}".format(time))
        
        return []




# FORM TO ANALYSE VOMITO
class VomitoForm(FormAction):
    """ Início do formulário """
    def name(self) -> Text:
        """ Nome único do formulário """
        return "vomito_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """ List de todos os slots que deverão ser preenchidos """
        return ["o_que_comeu", "o_que_aconteceu_depois", "quando_foi_isso"]
        # return ["o_que_comeu", "o_que_aconteceu_depois", "time"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        """ Um dicionário para mapear todos os slots necessário para:
        - extrair entidades
        - intenções
        - mensagem inteira
        ou uma lista de item,  """

        return{            
            "o_que_comeu":[
                self.from_entity(entity="o_que_comeu"),
                self.from_text()
            ],
            "o_que_aconteceu_depois":[
                self.from_entity(entity="o_que_aconteceu_depois"),
                self.from_text()
            ],
            "quando_foi_isso":[
                self.from_entity(entity="quando_foi_isso"),
                self.from_text()
            ]
        }


    def validate_o_que_comeu(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando o que comeu depois de vomitar """
        
        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"o_que_comeu":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"o_que_comeu": None}


    def validate_o_que_aconteceu_depois(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validando sintoma - o que aconteceu depois """ 

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"o_que_aconteceu_depois":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"o_que_aconteceu_depois": None}



    def validate_quando_foi_isso(self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> Dict[Text, Any]:
        """ Validação para extrair data - 'quando foi isso' """

        if re.findall(r"([a-zA-Z])\D*([a-zA-Z])$", value):
            return {"quando_foi_isso":value}
        else:
            # se não foi encontrado, slot recebe None, disparada a mensagem e será perguntado novamente
            dispatcher.utter_message("Acho que não entendi")
            return {"quando_foi_isso": None}

        # # date_input = value
        # tempo = tracker.get_slot("tempo")
        # dia_extraido = tracker.get_slot("dia")
        # user_input = value
        # dia = date.today().day
        # mes = date.today().month
        # ano = date.today().year

        # if (tempo == "hoje" or tempo == "hj"):
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "agora" or tempo == "a noite" or tempo == "à noite" or tempo == "de noite" or tempo == "a tarde" or tempo == "à tarde" or tempo == "de tarde" or tempo == "de manhã" or tempo == "pela manha" or tempo == "manha" or tempo == "manhã"):
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "ontem" or tempo == "onti" or tempo == "ante ontem" or tempo == "antes de ontem"):
        #     dia -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (dia_extraido == "domingo" or dia_extraido == "segunda" or dia_extraido == "terça" or dia_extraido == "terca" or dia_extraido == "quarta" or dia_extraido == "quinta" or dia_extraido == "sexta" or dia_extraido == "sabado" or dia_extraido == "sábado"):
        #     dia -= 7
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "semana" or tempo == "semana passada" or tempo == "semanas"):
        #     dia -= 7
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "mes" or tempo == "mês" or tempo == "mes passado" or tempo == "mês passado" or tempo == "meses"):
        #     mes -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # if (tempo == "ano" or tempo == "ano passado" or tempo == "anos"):
        #     ano -= 1
        #     data_extraida = "paciente disse: '{}', data aproximada: {}/{}/{}".format(user_input, dia, mes, ano)
        #     return{"quando_foi_isso":data_extraida}

        # else:
        #     data_extraida = "paciente disse: '{}', não consegui estipular data aproximada.".format(user_input)
        #     return{"quando_foi_isso":data_extraida}



    def submit(self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        ) -> List[Dict]:
        """ Depois de ter coletado todos os slots, fazer o submit """

        # coletando dados e salvando em variáveis

        o_que_comeu = tracker.get_slot("o_que_comeu")
        o_que_aconteceu_depois = tracker.get_slot("o_que_aconteceu_depois")
        # quando_foi_isso = tracker.get_slot("quando_foi_isso")
        quando_foi_isso = tracker.get_slot("quando_foi_isso")

        # printar mensagem de sucesso  
        dispatcher.utter_message("Certo! Confirmando queixa vomitar: \nComeu: {} \nAconteceu depois: {} \nQuando foi isso: {} \nOk, tudo certo! Vou repassar as informações ao médico para continuarmos sua consulta.".format(o_que_comeu, o_que_aconteceu_depois, quando_foi_isso))

        
        return []
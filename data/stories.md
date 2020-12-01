## caminho completo afirmativo da febre
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_febre
  - utter_ask_quando_comecou
* dias_febre
  - utter_ask_comecou_repente
* afirmacao
  - utter_febre_subito
  - utter_ask_foi_aferida
* afirmacao
  - utter_ask_qual_temperatura
* temperatura_febre
  - utter_ask_febre_periodo
* afirmacao
  - utter_desenvolvimento_joao
  - utter_ask_usou_medicacao
* afirmacao
  - utter_usou_antipiretico
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo negativo da febre
* cumprimentar
  - utter_saldacao
* negacao
  - utter_definicao_anamnese
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_febre
  - utter_ask_quando_comecou
* dias_febre
  - utter_ask_comecou_repente
* negacao
  - utter_febre_gradual
  - utter_ask_foi_aferida
* negacao
  - utter_nao_aferida
  - utter_ask_febre_periodo
* negacao
  - utter_febre_continua
  - utter_ask_usou_medicacao
* negacao
  - utter_nao_usou_antipiretico
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo afirmativo outros sintomas
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* outros_sintomas
  - utter_sintoma_nao_tratado
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo negativo de outros sintomas
* cumprimentar
  - utter_saldacao
* negacao
  - utter_definicao_anamnese
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* outros_sintomas
  - utter_sintoma_nao_tratado
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo afirmativo da dor
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_dor
  - dor_form
  - form{"name":"dor_form"}
  - form{"name":null}
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo negativo da dor
* cumprimentar
  - utter_saldacao
* negacao
  - utter_definicao_anamnese
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_dor
  - dor_form
  - form{"name":"dor_form"}
  - form{"name":null}
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo afirmativo paciente não sente nada
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* negacao
  - utter_sintoma_nao_tratado
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo afirmativo vomito
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_vomito
  - vomito_form
  - form{"name":"vomito_form"}
  - form{"name":null}
  - utter_obrigado
* obrigado
  - utter_tchau

## caminho completo negativo vomito
* cumprimentar
  - utter_saldacao
* negacao
  - utter_definicao_anamnese
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_vomito
  - vomito_form
  - form{"name":"vomito_form"}
  - form{"name":null}
  - utter_obrigado
* obrigado
  - utter_tchau
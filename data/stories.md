## caminho completo afirmativo da febre
* cumprimentar
  - utter_saldacao
* afirmacao
  - dados_form
  - form{"name":"dados_form"}
  - form{"name":null}
  - utter_o_que_aconteceu
* sintoma_febre
  - febre_form
  - form{"name":"febre_form"}
  - form{"name":null}
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
  - febre_form
  - form{"name":"febre_form"}
  - form{"name":null}
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
(fn BaseNext ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniNB) 1)
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 1) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniLastCK) 3) 1)))
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 2) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniLastCK) 3) 2)))
      (Funzionedichiamata|Done))
    (:else
      (Variabili|Predefinito|ImpostaStage 3)
      (Funzionedichiamata|FillPick))))

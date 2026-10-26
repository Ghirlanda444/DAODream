(fn PickCond (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 3) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 1) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K) 3) 1)))
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 2) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTConds) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K) 3) 2)))
      (Funzionedichiamata|Done))))

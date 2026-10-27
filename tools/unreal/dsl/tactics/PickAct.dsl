(fn PickAct (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 4) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 3) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptCmd) K))
      (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniRows) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniEditRow) 6) 4) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptSub) K))
      (Funzionedichiamata|Done))))

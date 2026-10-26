(fn PickAct (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 4) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Funzionedichiamata|SetAct :V (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K))
      (Funzionedichiamata|Done))))

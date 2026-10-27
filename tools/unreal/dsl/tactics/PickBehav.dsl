(fn PickBehav (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 6) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Variabili|Predefinito|ImpostaMBeh (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K))
      (Funzionedichiamata|SetBehOf)
      (Funzionedichiamata|DrawSetup)
      (Funzionedichiamata|ClosePick))))

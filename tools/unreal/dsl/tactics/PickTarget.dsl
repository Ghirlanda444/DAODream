(fn PickTarget (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 1) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Funzionedichiamata|SetTargetRow :V (Matematica|Conversioni|ToFloat(Integer) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K)))
      (Funzionedichiamata|Done))))

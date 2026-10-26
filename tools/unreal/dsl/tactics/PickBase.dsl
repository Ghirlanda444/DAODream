(fn PickBase (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 2) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Variabili|Predefinito|ImpostaBaseId (Matematica|Conversioni|ToFloat(Integer) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K)))
      (Funzionedichiamata|CountBase)
      (Funzionedichiamata|BaseNext))))

(fn PickPreset (K)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniStageNow) 5) (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniOptIds))))
    (:then
      (Variabili|Predefinito|ImpostaPresetIdx (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniOptIds) K))
        (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniRows)) 1)
    (:LoopBody
      (Funzionedichiamata|ZeroAt :J _index))
    (:Completed
      (Funzionedichiamata|FillPreset))))))

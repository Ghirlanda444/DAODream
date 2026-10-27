(fn FillPreset ()
  (Variabili|Predefinito|ImpostaAdded 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Matematica|Float|Truncate (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTPresets) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniPresetIdx) 6) 5))) 1)
    (:LoopBody
      (Funzionedichiamata|PresetRow :J _index))
    (:Completed
      (Funzionedichiamata|Done))))

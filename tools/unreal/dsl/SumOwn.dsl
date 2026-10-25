(fn SumOwn ()
  (Variabili|Predefinito|ImpostaOwnAtk 0.0)
  (Variabili|Predefinito|ImpostaOwnPen 0.0)
  (Variabili|Predefinito|ImpostaOwnSpeed 0.0)
  (Variabili|Predefinito|ImpostaOwnCrit 0.0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
    (:LoopBody
      (Funzionedichiamata|AddOwn :Slot _index))
    (:Completed
      (Variabili|Predefinito|ImpostaPInterval (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniPBaseInterval) (Matematica|Float|Clamp(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniOwnSpeed) 1.0) 0.5 1.5))))))

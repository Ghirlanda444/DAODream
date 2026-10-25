(fn NSumOwn ()
  (Variabili|Predefinito|ImpostaNBaseInterval (Matematica|Float|SelectFloat (Variabili|Predefinito|OttieniInterval) (Variabili|Predefinito|OttieniNBaseInterval) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniNBaseInterval) 0.0)))
  (Variabili|Predefinito|ImpostaNOwnAtk 0.0)
  (Variabili|Predefinito|ImpostaNOwnSpeed 0.0)
  (Variabili|Predefinito|ImpostaNOwnCrit 0.0)
  (Variabili|Predefinito|ImpostaNOwnDef 0.0)
  (Variabili|Predefinito|ImpostaNOwnArmour 0.0)
  (Variabili|Predefinito|ImpostaNOwnScale 0.0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniNOn)) 1)
    (:LoopBody
      (Funzionedichiamata|NAddOwn :K _index))
    (:Completed
      (Variabili|Predefinito|ImpostaInterval (Utility|Operatori|Moltiplica (Variabili|Predefinito|OttieniNBaseInterval) (Matematica|Float|Clamp(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnSpeed) 1.0) 0.5 1.5))))))

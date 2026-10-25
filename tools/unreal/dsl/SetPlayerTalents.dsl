(fn SetPlayerTalents (InTalents InPassives InNames)
  (Variabili|Predefinito|ImpostaTalents InTalents)
  (Variabili|Predefinito|ImpostaPassives InPassives)
  (Variabili|Predefinito|ImpostaTalentNames InNames)
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniTReady))
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniTUntil))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length InNames) 1)
    (:LoopBody
      (Utilità|Array|Add (Variabili|Predefinito|OttieniTReady) 0.0)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniTUntil) 0.0))
    (:Completed
      (Funzionedichiamata|ShowTalents))))

(fn ModeOff (Ability)
  (Variabili|Predefinito|ImpostaTFound -1)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex 5
    (:LoopBody
      (Funzionedichiamata|FindOne :K _index :Ability Ability))
    (:Completed
      (Funzionedichiamata|ModeOffGo))))

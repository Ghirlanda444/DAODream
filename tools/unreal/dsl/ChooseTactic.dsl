(fn ChooseTactic ()
  (Variabili|Predefinito|ImpostaTacSlot -1)
  (Variabili|Predefinito|ImpostaTacNext 0.0)
  (Variabili|Predefinito|ImpostaTacDone "false")
  (Funzionedichiamata|ReadFoe)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utility|Operatori|Dividi (Utilità|Array|Length (Variabili|Predefinito|OttieniNTactics)) 6) 1)
    (:LoopBody
      (Funzionedichiamata|TacticRow :I _index))))

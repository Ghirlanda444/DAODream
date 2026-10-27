(fn TrInsNear (D)
  (Variabili|Predefinito|ImpostaPkIns 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniNearD)) 1)
    (:LoopBody
      (Funzionedichiamata|TrInsNearLess :K _index :D D))
    (:Completed
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniNearD) D (Variabili|Predefinito|OttieniPkIns))
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniNearDead) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniPkAlive)) (Variabili|Predefinito|OttieniPkIns)))))

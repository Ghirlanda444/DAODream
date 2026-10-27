(fn TrInsEn (A D)
  (Utilità|Array|Add (Variabili|Predefinito|OttieniEnAll) A)
  (Variabili|Predefinito|ImpostaRingN (Matematica|Intero|SelectInt (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniRingN) 1) (Variabili|Predefinito|OttieniRingN) (Utility|Operatori|Minoreuguale(<=) D 250.0)))
  (Variabili|Predefinito|ImpostaPkIns 0)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniEnD)) 1)
    (:LoopBody
      (Funzionedichiamata|TrInsEnLess :K _index :D D))
    (:Completed
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniEnL) A (Variabili|Predefinito|OttieniPkIns))
      (Utilità|Array|Insert (Variabili|Predefinito|OttieniEnD) D (Variabili|Predefinito|OttieniPkIns)))))

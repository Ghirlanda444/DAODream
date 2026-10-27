(fn TacItem2 (Me Cmd Sub)
  (Funzionedichiamata|TrPeek :A Me)
  (Variabili|Predefinito|ImpostaTIt -1)
  (Variabili|Predefinito|ImpostaGBest 0.0)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) Cmd 15.0) (Utility|Operatori|Uguale(==) Cmd 16.0)) (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniPkHp) (Variabili|Predefinito|OttieniPkMax)))
    (:else
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniInv)) 1)
    (:LoopBody
      (Funzionedichiamata|TacItemOne :K _index :Cmd Cmd :Sub Sub))
    (:Completed
      (Funzionedichiamata|TacItemUse :Me Me))))))

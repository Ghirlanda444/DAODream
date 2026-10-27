(fn HeroTacticTalent (I)
  (Variabili|Predefinito|ImpostaHTFound -1)
  (Variabili|Predefinito|ImpostaHTStop "false")
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
    (:LoopBody
      (Funzionedichiamata|HeroFindTalent :K _index :Sub (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 4))))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniHTFound) 0)
    (:then
      (Funzionedichiamata|HeroTacticFire :bMode (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 3)) 5.0)))))))

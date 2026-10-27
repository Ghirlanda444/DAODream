(fn HeroModeOff (I)
  (Variabili|Predefinito|ImpostaHTFound -1)
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames)) 1)
    (:LoopBody
      (Funzionedichiamata|HeroFindTalent :K _index :Sub (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 4))))
    (:Completed
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniHTFound) 0) (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniHTFound)) 100000000.0))
    (:then
      (Variabili|Predefinito|ImpostaTSlot (Variabili|Predefinito|OttieniHTFound))
      (Funzionedichiamata|ToggleSustained)
      (Variabili|Predefinito|ImpostaHTDone "true"))))))

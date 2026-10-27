(fn HeroItem (I)
  (Funzionedichiamata|TacItem :Me (Gioco|GetPlayerPawn 0) :Cmd (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 3)) :Sub (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniPTactics) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica I 6) 4)))
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniBF)
    (:then
      (Variabili|Predefinito|ImpostaHTDone "true"))))

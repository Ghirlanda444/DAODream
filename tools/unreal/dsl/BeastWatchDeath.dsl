(fn WatchDeath (Npc)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniDead Npc)
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniFallen)
        (:then
          (Variabili|Predefinito|ImpostaDeathTime (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniDeathTime) (Utilità|Testo|GetWorldDeltaSeconds))))
        (:else
          (Variabili|Predefinito|ImpostaDeathTime (Matematica|Float|SelectFloat 0.0 10.0 (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastHealth) 0.0)))
          (Variabili|Predefinito|ImpostaFallen "true"))))
    (:else
      (Variabili|Predefinito|ImpostaFallen "false"))))

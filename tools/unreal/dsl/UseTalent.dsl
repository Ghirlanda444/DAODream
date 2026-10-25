(fn UseTalent (Slot)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniTalking) (Variabili|Predefinito|OttieniGameOver)) (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPlayerDown) (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggioreuguale(>=) Slot (Utilità|Array|Length (Variabili|Predefinito|OttieniTalentNames))) (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPStunUntil) (Utilità|Testo|GetGameTimeinSeconds)) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniPLockUntil) (Utilità|Testo|GetGameTimeinSeconds))))))
    (:else
      (Funzionedichiamata|TalentCheck :Slot Slot))))

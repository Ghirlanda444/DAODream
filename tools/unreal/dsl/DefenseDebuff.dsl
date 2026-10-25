(fn DefenseDebuff (Amount Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Variabili|Predefinito|OttieniResist))
    (:then
      (Funzionedichiamata|SayText :Txt "Resisted"))
    (:else
      (Variabili|Predefinito|ImpostaNDefAdd Amount)
      (Variabili|Predefinito|ImpostaNDefUntil (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds))
      (Funzionedichiamata|SayText :Txt "Defense down"))))

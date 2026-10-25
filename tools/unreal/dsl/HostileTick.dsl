(fn HostileTick (Dt)
  (Variabili|Predefinito|ImpostaNStamina (Matematica|Float|Min(Float) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNStamina) Dt) (Variabili|Predefinito|OttieniNPool)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniStunUntil) (Variabili|Predefinito|OttieniKnockUntil)) (Utilità|Testo|GetGameTimeinSeconds))
    (:else
      (Funzionedichiamata|Recover)
      (Funzionedichiamata|HostileTurn :Dt Dt))))

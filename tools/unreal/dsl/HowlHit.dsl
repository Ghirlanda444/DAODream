(fn HowlHit (From bPartySide Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniDead)) (Matematica|Booleano|NOTBoolean (Variabili|Rendering|OttieniActorHiddenInGame))) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Trasformazione|GetDistanceTo (Variabili|Ottieniunriferimentoasestesso) From) 1000.0) (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniDurScale) 0.78) (Matematica|Booleano|ORBoolean (Matematica|Booleano|ANDBoolean bPartySide (Variabili|Predefinito|OttieniHostile)) (Matematica|Booleano|ANDBoolean (Matematica|Booleano|NOTBoolean bPartySide) (Variabili|Predefinito|OttieniInParty))))))
    (:then
      (Variabili|Predefinito|ImpostaStunUntil (Matematica|Float|Max(Float) (Variabili|Predefinito|OttieniStunUntil) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds)))
      (Funzionedichiamata|StopMoving)
      (Funzionedichiamata|SayText :Txt "Stunned"))))

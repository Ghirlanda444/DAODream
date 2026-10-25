(fn Knock (Seconds)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica (Matematica|Casuale|RandomFloat) 100.0) (Variabili|Predefinito|OttieniResist))
    (:then
      (Funzionedichiamata|SayText :Txt "Resisted"))
    (:else
      (Variabili|Predefinito|ImpostaKnockUntil (Utility|Operatori|Aggiungi (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) Seconds) (Matematica|Casuale|RandomFloat)))
      (Variabili|Predefinito|ImpostaKnocked "true")
      (Variabili|Predefinito|ImpostaChasing "false")
      (Funzionedichiamata|StopMoving)
      (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) "/Game/Cousland/Anims/A_Fallen.A_Fallen" "false")
      (Funzionedichiamata|SayText :Txt "Knocked down"))))

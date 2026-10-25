(fn StopChase ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniChasing)
    (:then
      (Variabili|Predefinito|ImpostaChasing "false")
      (Funzionedichiamata|StopMoving)
      (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle" "true"))))

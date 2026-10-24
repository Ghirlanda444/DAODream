(fn GetUp ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniDown)
    (:then
      (Variabili|Predefinito|ImpostaDown "false")
      (Variabili|Predefinito|ImpostaDead "false")
      (Variabili|Predefinito|ImpostaHealth 1.0)
      (Funzionedichiamata|ShowPartyBar)
      (Variabili|Predefinito|ImpostaIdleAnim "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle")
      (Componenti|Animazione|PlayAnimation (Variabili|Predefinito|OttieniMesh) "/Game/Characters/Mannequins/Anims/Unarmed/MM_Idle.MM_Idle" "true"))))

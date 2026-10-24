(fn RevivePlayer ()
  (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPlayerDown)
    (:then
      (Variabili|Predefinito|ImpostaPlayerDown "false")
      (Variabili|Predefinito|ImpostaPlayerHealth 1.0)
      (Funzionedichiamata|ShowHealth)
      (Input|EnableInput (Gioco|GetPlayerPawn 0) (Gioco|GetPlayerController 0))
      (bind _mesh (Utilità|Casting|CastToSkeletalMeshComponent (Attore|GetComponentbyClass (Gioco|GetPlayerPawn 0) "/Script/Engine.SkeletalMeshComponent")))
      (Componenti|Animazione|SetAnimationMode _mesh "AnimationBlueprint"))))

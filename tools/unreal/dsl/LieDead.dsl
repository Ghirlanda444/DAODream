(fn LieDead ()
  (bind _cls (Utilità|GetClassDisplayName (Utilità|GetClass (Variabili|Predefinito|OttieniLook))))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniLook)) (Matematica|Booleano|ORBoolean (Utilità|Stringa|Contains _cls "Mabari") (Utilità|Stringa|Contains _cls "GiantRat")))
    (:then
      (Variabili|Predefinito|ImpostaNear "false")
      (Collisione|SetActorEnableCollision (Variabili|Ottieniunriferimentoasestesso) "false")
      (Spunta|attore|SetActorTickEnabled (Variabili|Ottieniunriferimentoasestesso) "false")
      (Sviluppo|SetHiddeninGame (Variabili|Predefinito|OttieniHealthWidget) "true")
      (Sviluppo|SetHiddeninGame (Variabili|Predefinito|OttieniNameText) "true"))
    (:else
      (Funzionedichiamata|SetPlotActive :bOn "false"))))

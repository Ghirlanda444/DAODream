(fn CommandThing (Where What)
  (Funzionedichiamata|PickDoorOf :What What)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickDoor))
    (:then
      (Variabili|Predefinito|ImpostaHeroUse What))
    (:else
      (Variabili|Predefinito|ImpostaMoveGoal Where)
      (Variabili|Predefinito|ImpostaMoving "true"))))

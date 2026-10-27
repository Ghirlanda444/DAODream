(fn CommandThing (Where What)
  (Funzionedichiamata|PickDoorOf :What What)
  (Funzionedichiamata|PickBoxOf :What What)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utilità|IsValid (Variabili|Predefinito|OttieniPickDoor)) (Utilità|IsValid (Variabili|Predefinito|OttieniPickBox)))
    (:then
      (Variabili|Predefinito|ImpostaHeroUse What))
    (:else
      (Variabili|Predefinito|ImpostaMoveGoal Where)
      (Variabili|Predefinito|ImpostaMoving "true"))))

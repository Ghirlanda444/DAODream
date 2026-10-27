(fn HeroBidGate ()
  (Funzionedichiamata|TrFlag :B (Variabili|Predefinito|OttieniPBehavior) :Fl 2)
  (Variabili|Predefinito|ImpostaBMayH (Matematica|Booleano|ORBoolean (Variabili|Predefinito|OttieniPartyMayAttack) (Variabili|Predefinito|OttieniBF)))
  (Funzionedichiamata|TrFlag :B (Variabili|Predefinito|OttieniPBehavior) :Fl 7)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniBMayH)) (Matematica|Booleano|NOTBoolean (Variabili|Predefinito|OttieniBF)))
    (:then
      (Variabili|Predefinito|ImpostaHeroTarget))))

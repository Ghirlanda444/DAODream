(fn TargetTalent ()
  (Funzionedichiamata|FindTarget)
  (Funzionedichiamata|CountParty)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget))
    (:then
      (Funzionedichiamata|PayTalent)
      (Funzionedichiamata|SwingAnim)
      (Funzionedichiamata|HitTalent)
      (Funzionedichiamata|ImpactThreat))
    (:else
      (Funzionedichiamata|ShowMsg :Txt "No target in reach"))))

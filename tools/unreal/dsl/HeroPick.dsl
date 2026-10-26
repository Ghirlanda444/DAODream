(fn HeroPick ()
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniHeroTarget))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniDead (Variabili|Predefinito|OttieniHeroTarget))
        (:then
          (Funzionedichiamata|HeroBid))))
    (:else
      (Funzionedichiamata|HeroBid))))

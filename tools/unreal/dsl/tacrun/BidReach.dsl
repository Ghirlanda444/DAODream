(fn BidReach (Follower)
  (Classe|BPDlgNPC|NFlag Follower :Fl 1)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minoreuguale(<=) (Trasformazione|GetHorizontalDistanceTo (Variabili|Predefinito|OttieniBestTarget) (Variabili|Predefinito|OttieniTCtrl)) (Matematica|Float|SelectFloat 3000.0 1500.0 (Classe|BPDlgNPC|OttieniBFlag Follower)))
    (:then
      (Classe|BPDlgNPC|SetTarget Follower :InTarget (Utilità|Casting|CastToBP_DlgNPC (Variabili|Predefinito|OttieniBestTarget))))
    (:else
      (Classe|BPDlgNPC|SetTarget Follower))))
